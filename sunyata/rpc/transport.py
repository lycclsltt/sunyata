from socket import *
import struct
from sunyata.rpc.const import SERVER_TIMEOUT
from sunyata.rpc.compress import RpcCompress
import aiohttp


class RpcTransport(object): 

    def close(self):
        pass


class TcpTransport(RpcTransport):

    __slots__ = ('host', 'port', 'timeout', 'socket', 'keepaliveTimeout')

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
        isEnableCompress = b'0'
        oldMsgLen = len(msg)
        oldMsg = msg
        if len(msg) >= RpcCompress.enableCompressLen:
            isEnableCompress = b'1'
            msg = RpcCompress.compress(msg)
            newMsgLen = len(msg)
            if newMsgLen > oldMsgLen:
                isEnableCompress = b'0'
                msg = oldMsg
        newbyte = struct.pack("i", len(msg))
        try:
            self.socket.sendall(newbyte + isEnableCompress + msg)
        except BrokenPipeError:
            self.reconnect()
            self.socket.sendall(newbyte + isEnableCompress + msg)

    def sendPeer(self, msg: bytes, conn):
        isEnableCompress = b'0'
        if len(msg) >= RpcCompress.enableCompressLen:
            isEnableCompress = b'1'
            msg = RpcCompress.compress(msg)
        newbyte = struct.pack("i", len(msg))
        conn.sendall(newbyte + isEnableCompress + msg)

    def getSendByte(self, msg: bytes, conn = None):
        newbyte = struct.pack("i", len(msg))
        ret = newbyte + msg
        return ret

    def recv(self):
        #每次读一个完整的字节，再接收前4个字节，再取body
        conn = self.socket
        toread = 5
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
        lengthField = lengthbyte[:4]
        compressField = lengthbyte[4:5]
        isEnableCompress = 0
        if compressField == b'1':
            isEnableCompress = 1
        toread = struct.unpack("i", lengthField)[0]
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
        if isEnableCompress:
            msg = RpcCompress.decompress(msg)
        return msg

    def recvPeer(self, conn):
        #每次读一个完整的字节，再接收前4个字节，再取body
        toread = 5
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
        lengthField = lengthbyte[:4]
        compressField = lengthbyte[4:5]
        isEnableCompress = 0
        if compressField == b'1':
            isEnableCompress = 1
        toread = struct.unpack("i", lengthField)[0]
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
        if isEnableCompress:
            msg = RpcCompress.decompress(msg)
        return msg

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def reconnect(self):
        self.close()
        self.connect()
        print('tcp client reconnect')


class UdpTransport(RpcTransport):

    __slots__ = ('host', 'port', 'socket', 'timeout')
    
    def __init__(self, host, port, timeout = SERVER_TIMEOUT):
        RpcTransport.__init__(self)
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = timeout
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.maxUdpPackageSize = 65535

    def bind(self):
        self.socket.bind( (self.host, self.port) )

    def sendPeer(self, msg: bytes, addr):
        isEnableCompress = b'0'
        if len(msg) >= RpcCompress.enableCompressLen:
            isEnableCompress = b'1'
            msg = RpcCompress.compress(msg)
        package = isEnableCompress + msg
        self.socket.sendto(package, addr)

    def send(self, msg: bytes):
        isEnableCompress = b'0'
        if len(msg) >= RpcCompress.enableCompressLen:
            isEnableCompress = b'1'
            msg = RpcCompress.compress(msg)
        if len(msg) >= self.maxUdpPackageSize:
            raise Exception('msg too long > udp allow size 65535')
        addr = (self.host, self.port)
        package = isEnableCompress + msg
        self.socket.sendto(package, addr)

    def recv(self, conn = None):
        if conn == None:
            conn = self.socket
        package, addr = conn.recvfrom(100000)
        isEnableCompress = package[:1]
        msg = package[1:]
        if isEnableCompress == b'1':
            msg = RpcCompress.decompress(msg)
        return msg, addr

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None


class ClientUdpTransport(UdpTransport):

    __slots__ = ('timeout')

    def __init__(self, host, port, timeout = 10):
        UdpTransport.__init__(self, host, port)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)


class HttpTransport(RpcTransport):

    def __init__(self, host, port, timeout = 10, poolConnection=20, poolMaxSize=20, maxRetries=2):
        RpcTransport.__init__(self)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.url = self.makeUrl()
        self.headers = {
            'Content-type' : 'application/octet-stream'
        }

    def makeUrl(self):
        return "http://%s:%s/" % (self.host, self.port)

    async def send(self, msg):
        isEnableCompress = b'0'
        if len(msg) >= RpcCompress.enableCompressLen:
            isEnableCompress = b'1'
            msg = RpcCompress.compress(msg)
        msg = isEnableCompress + msg
        async with aiohttp.ClientSession() as sess:
            async with sess.post(self.url, headers = {}, data=msg, timeout = self.timeout) as r:
                content = await r.read()
                return content