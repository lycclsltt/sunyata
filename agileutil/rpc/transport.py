#coding=utf-8

from socket import *
import struct
from agileutil.sanic import SanicApp
from multiprocessing import cpu_count
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from agileutil.rpc.const import SERVER_TIMEOUT


class RpcTransport(object): 

    def close(self):
        pass


class TcpTransport(RpcTransport):

    def __init__(self, host, port, timeout):
        RpcTransport.__init__(self)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.keepaliveTimeout = SERVER_TIMEOUT

    def bind(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind( (self.host, self.port) )
        self.socket.listen(100)

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

    def send(self, msg: bytes):
        newbyte = struct.pack("i", len(msg))
        try:
            self.socket.sendall(newbyte)
            self.socket.sendall(msg)
        except BrokenPipeError:
            self.reconnect()
            self.socket.sendall(newbyte)
            self.socket.sendall(msg)

    def sendPeer(self, msg: bytes, conn):
        newbyte = struct.pack("i", len(msg))
        conn.sendall(newbyte)
        conn.sendall(msg)

    def getSendByte(self, msg: bytes, conn = None):
        newbyte = struct.pack("i", len(msg))
        ret = newbyte + msg
        return ret

    def recv(self):
        #每次读一个完整的字节，再接收前4个字节，再取body
        conn = self.socket
        toread = 4
        readn = 0
        lengthbyte = b''
        while 1:
            bufsize = toread - readn
            if bufsize <= 0:
                break
            bytearr = conn.recv(bufsize)
            if len(bytearr) == 0:
                raise Exception('peer closed')
            lengthbyte = lengthbyte + bytearr
            readn = readn + len(bytearr)
        toread = struct.unpack("i", lengthbyte)[0]
        readn = 0
        msg = b''
        while 1:
            bufsize = toread - readn
            if bufsize <= 0:
                break
            bytearr = conn.recv(bufsize)
            if len(bytearr) == 0:
                raise Exception('peer closed')
            msg = msg + bytearr
            readn = readn + len(bytearr)
        return msg

    def recvPeer(self, conn):
        #每次读一个完整的字节，再接收前4个字节，再取body
        toread = 4
        readn = 0
        lengthbyte = b''
        while 1:
            bufsize = toread - readn
            if bufsize <= 0:
                break
            bytearr = conn.recv(bufsize)
            if len(bytearr) == 0:
                raise Exception('peer closed')
            lengthbyte = lengthbyte + bytearr
            readn = readn + len(bytearr)
        toread = struct.unpack("i", lengthbyte)[0]
        readn = 0
        msg = b''
        while 1:
            bufsize = toread - readn
            if bufsize <= 0:
                break
            bytearr = conn.recv(bufsize)
            if len(bytearr) == 0:
                raise Exception('peer closed')
            msg = msg + bytearr
            readn = readn + len(bytearr)
        return msg

    def close(self):
        self.socket.close()
        self.socket = None

    def reconnect(self):
        self.close()
        self.connect()
        print('tcp client reconnect')


class UdpTransport(RpcTransport):
    
    def __init__(self, host, port, timeout = SERVER_TIMEOUT):
        RpcTransport.__init__(self)
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = timeout
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    def bind(self):
        self.socket.bind( (self.host, self.port) )

    def sendPeer(self, msg: bytes, addr):
        self.socket.sendto(msg, addr)

    def send(self, msg: bytes):
        addr = (self.host, self.port)
        self.socket.sendto(msg, addr)

    def recv(self, conn = None):
        if conn == None:
            conn = self.socket
        msg, addr = conn.recvfrom(100000)
        return msg, addr

    def close(self):
        self.socket.close()
        self.socket = None


class ClientUdpTransport(UdpTransport):

    def __init__(self, host, port, timeout = 10):
        UdpTransport.__init__(self, host, port)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)


class HttpTransport(RpcTransport):

    def __init__(self, host, port, worker=cpu_count(), timeout = 10, poolConnection=20, poolMaxSize=20, maxRetries=2):
        RpcTransport.__init__(self)
        self.host = host
        self.port = port
        self.worker = worker
        self.timeout = timeout
        self.app = SanicApp(host=host, port=port, worker_num=worker, debug=False)
        self.poolConnection = poolConnection
        self.poolMaxSize = poolMaxSize
        self.maxRetries = maxRetries
        self.requestSession = requests.Session()
        self.requestSession.mount('http://', requests.adapters.HTTPAdapter(pool_connections=self.poolConnection, pool_maxsize=self.poolMaxSize, max_retries=self.maxRetries))
        self.url = self.makeUrl()
        self.headers = {
            'Content-type' : 'application/octet-stream'
        }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def makeUrl(self):
        return "http://%s:%s/" % (self.host, self.port)

    def send(self, msg):
        r = self.requestSession.post(self.url, headers = self.headers, data=msg, timeout = self.timeout)
        resp = r.content
        return resp