#coding=utf-8

import zmq

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