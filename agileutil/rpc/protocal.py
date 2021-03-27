#coding=utf-8

from agileutil.rpc.transport import TcpTransport, UdpTransport, HttpTransport, ClientUdpTransport, RpcTransport
from agileutil.rpc.serialize import BinarySerialize, JsonSerialize, RpcSerialize
import json
from abc import ABCMeta, abstractmethod
from agileutil.sanic import SanicApp
from multiprocessing import cpu_count
import requests


class RpcProtocal(object):

    def __init__(self):
        self.transport = RpcTransport()

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

    def tranArgs(self, args):
        nargs = tuple()
        if args == None:
            return nargs
        if type(args) != tuple and type(args) != list:
            nargs = (args, )
        else:
            nargs = tuple(args)
        return nargs


class UdpProtocal(RpcProtocal):

    def __init__(self):
        pass


class HttpProtocal(RpcProtocal):

    def __init__(self, host, port, worker = cpu_count(), serializeType = 'bin', timeout = 10, poolConnection=5, poolMaxSize = 20, maxRetries = 3):
        RpcProtocal.__init__(self)
        self.host = host
        self.port = port
        self.worker = worker
        self.serializeType = serializeType
        self.timeout = timeout
        self.transport = HttpTransport(host, port, worker, timeout, poolConnection, poolMaxSize, maxRetries)


class TcpProtocal(RpcProtocal):
    
    def __init__(self, host, port, serializeType = 'bin', timeout = 10):
        RpcProtocal.__init__(self)
        self.serializeType = serializeType
        self.timeout = timeout
        self.transport = TcpTransport(host, port, timeout)


class UdpProtocal(RpcProtocal):

    def __init__(self, host, port, serializeType = 'bin', timeout = 10):
        RpcProtocal.__init__(self)
        self.serializeType = serializeType
        self.timeout = timeout
        self.transport = UdpTransport(host, port)


class ClientUdpProtocal(UdpProtocal):

    def __init__(self, host, port, serializeType = 'bin', timeout = 10):
        UdpProtocal.__init__(self, host, port, serializeType=serializeType, timeout=timeout)
        self.serializeType = serializeType
        self.host = host
        self.port = port
        self.timeout = timeout
        self.transport = ClientUdpTransport(host, port, timeout)
    
    def newTransport(self):
        self.transport.close()
        self.transport = ClientUdpTransport(self.host, self.port, self.timeout)