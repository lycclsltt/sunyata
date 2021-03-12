#coding=utf-8

from agileutil.rpc.transport import ZMQTransport, TcpTransport, UdpTransport
from agileutil.rpc.serialize import BinarySerialize, JsonSerialize, RpcSerialize
import json
from abc import ABCMeta, abstractmethod


class RpcProtocal(object):

    def __init__(self):
        pass

    def serialize(self, obj):
        serializer = None
        if self.serializeType == 'bin':
            serializer = BinarySerialize()
        elif self.serializeType == 'json':
            serializer = JsonSerialize()
        if serializer == None:
            raise Exception('unknown serializeType')
        return serializer.serialize(obj)

    def unserialize(self, msg):
        serializer = None
        if self.serializeType == 'bin':
            serializer = BinarySerialize()
        elif self.serializeType == 'json':
            serializer = JsonSerialize()
        if serializer == None:
            raise Exception('unknown serializeType')
        return serializer.unserialize(msg) 

    def parseRequest(self, package):
        func = package['func']
        args = package['args']
        return func, args


class UdpProtocal(RpcProtocal):

    def __init__(self):
        pass


class HttpProtocal(RpcProtocal):

    def __init__(self):
        pass


class TcpProtocal(RpcProtocal):
    
    def __init__(self, host, port, serializeType = 'bin'):
        RpcProtocal.__init__(self)
        self.serializeType = serializeType
        self.transport = TcpTransport(host, port)


class UdpProtocal(RpcProtocal):

    def __init__(self, host, port, serializeType = 'bin'):
        RpcProtocal.__init__(self)
        self.serializeType = serializeType
        self.transport = UdpTransport(host, port)