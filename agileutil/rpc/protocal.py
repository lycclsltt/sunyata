#coding=utf-8

from agileutil.rpc.transport import ZMQTransport
from agileutil.rpc.serialize import BinarySerialize, JsonSerialize, RpcSerialize
import json
from abc import ABCMeta, abstractmethod


class RpcProtocal(object):
    
    __metaclass__ = ABCMeta

    def __init__(self):
        pass


class UdpProtocal(RpcProtocal):

    def __init__(self):
        pass


class HttpProtocal(RpcProtocal):
    def __init__(self):
        pass


class TcpProtocal(RpcProtocal):
    
    def __init__(self, host, port, serializeType = 'bin'):
        self.transport = ZMQTransport(host, port)
        self.serializeType = serializeType

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