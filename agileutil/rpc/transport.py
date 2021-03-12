#coding=utf-8

import zmq
from socket import *
import struct

class RpcTransport(object): pass


class ZMQTransport(RpcTransport):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.context = None
        self.socket = None
        self.connstr = 'tcp://%s:%s' % (self.host, self.port)

    def bind(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.connstr)

    def connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.connstr)

    def recv(self):
        msg = self.socket.recv()
        return msg

    def send(self, msg: bytes):
        self.socket.send(msg)


class TcpTransport(RpcTransport):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def bind(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind( (self.host, self.port) )
        self.socket.listen(100)

    def connect(self):
        if self.socket == None:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.connect( (self.host, self.port) )

    def accept(self):
        cli, addr = self.socket.accept()
        return cli, addr

    def send(self, msg: bytes, conn = None):
        if conn == None:
            conn = self.socket
        newbyte = struct.pack("i", len(msg))
        conn.sendall(newbyte)
        conn.sendall(msg)

    def getSendByte(self, msg: bytes, conn = None):
        newbyte = struct.pack("i", len(msg))
        ret = newbyte + msg
        return ret

    def recv(self, conn = None):
        #每次读一个完整的字节，再接收前4个字节，再取body
        if conn == None:
            conn = self.socket
        toread = 4
        readn = 0
        lengthbyte = b''
        while 1:
            bufsize = toread - readn
            if bufsize <= 0:
                break
            bytearr = conn.recv(bufsize)
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
            msg = msg + bytearr
            readn = readn + len(bytearr)
        return msg

    def close(self):
        self.socket.close()
        self.socket = None


class UdpTransport(RpcTransport):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    def bind(self):
        self.socket.bind( (self.host, self.port) )

    def send(self, msg: bytes, conn = None, addr = None):
        if conn == None:
            conn = self.socket
        if addr == None:
            addr = (self.host, self.port)
        conn.sendto(msg, addr)

    def recv(self, conn = None):
        if conn == None:
            conn = self.socket
        msg, addr = conn.recvfrom(100000)
        return msg, addr

    def close(self):
        self.socket.close()
        self.socket = None