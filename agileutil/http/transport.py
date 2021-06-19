from socket import *

class TcpTransport(object):

    __slots__ = ('host', 'port', 'timeout', 'socket', 'keepaliveTimeout', 'backlog')

    def __init__(self, host, port, timeout = 30, keepaliveTimeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.keepaliveTimeout = keepaliveTimeout
        self.backlog = 100

    def bind(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind( (self.host, self.port) )
        self.socket.listen(self.backlog)

    def setKeepaliveTimeout(self, keepaliveTimeout: int):
        self.keepaliveTimeout = keepaliveTimeout

    def connect(self):
        if self.socket == None:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket.connect( (self.host, self.port) )

    def accept(self):
        cli, addr = self.socket.accept()
        cli.settimeout(self.keepaliveTimeout)
        return cli, addr

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def reconnect(self):
        self.close()
        self.connect()
        print('tcp client reconnect')

    def recvUntil(self, conn, until):
        retbytearr = b''
        index = 0 - len(until)
        while True:
            rbytes = conn.recv(1)
            if rbytes == b'':
                break
            retbytearr += rbytes
            if retbytearr[index:] == until:
                break
        return retbytearr

    def recvFullHeader(self, conn):
        fullbytes = b''
        while True:
            rbytes = self.recvUntil(conn, b'\r\n')
            fullbytes += rbytes
            if rbytes == b'\r\n' or rbytes == b'':
                break
        return fullbytes

    def recvn(self, conn, n):
        toRecv = n
        hasRecv = 0
        bytearr = b''
        while True:
            if hasRecv >= toRecv:
                break
            bytearr += conn.recv(1)
            hasRecv += 1
        return bytearr

    def sendAll(self, conn, bytearr):
        toSend = len(bytearr)
        while toSend > 0:
            toSend -= conn.send(bytearr)
            bytearr = bytearr[0-toSend:] 