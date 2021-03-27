#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal, UdpProtocal, HttpProtocal, RpcProtocal, ClientUdpProtocal
from agileutil.rpc.exception import FuncNotFoundException
from agileutil.rpc.discovery import DiscoveryConfig
from agileutil.rpc.discovery import ConsulRpcDiscovery
from agileutil.wrap import retryTimes
from agileutil.rpc.discovery import Instance
import socket

class Address(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port


class RpcClient(object): 

    def __init__(self):
        self.discoveryConfig = None
        self.discovery = None
        self.instanceIndex = 0
        self.protocalMap = {}
        self.isSync = False
        self.syncInterval = 30
        self.protocal = RpcProtocal()
        self.servers = []
        self.serversCount = len(self.servers)
        self.serversProtocalMap = {}
        self.serverIndex = 0
        self.lastServer = ''
        self.timeout = 10

    def getInstance(self):
        instanceList = self.discovery.getInstanceList(self.discoveryConfig.serviceName)
        instanceLength  = len(instanceList)
        if instanceLength == 0:
            raise Exception('no instance found')
        index = self.instanceIndex % instanceLength
        self.instanceIndex = self.instanceIndex + 1
        return instanceList[index]

    def refreshProtocal(self):
        if self.discovery:
            instance = self.getInstance()
            self.protocal = self.getProtocalInstance(instance)
        if self.servers:
            self.serversCount = len(self.servers)
            index = self.serverIndex % self.serversCount
            self.serverIndex = self.serverIndex + 1
            server = self.servers[ index ]
            self.lastServer = server
            self.protocal = self.serversProtocalMap[ server ]

    def getProtocalInstance(self, instance):
        #overide
        pass

    def setDiscoveryConfig(self, config: DiscoveryConfig):
        self.discoveryConfig = config
        self.discovery = ConsulRpcDiscovery(self.discoveryConfig.consulHost, self.discoveryConfig.consulPort)

    def close(self):
        self.protocal.transport.close()

    def __del__(self):
        self.close()

    def beforeCall(self):
        self.refreshProtocal()

    def debugGetLastServer(self):
        return self.lastServer


class TcpRpcClient(RpcClient):

    def __init__(self, host = '', port = 0, servers=[], timeout=10, keepconnect = True):
        RpcClient.__init__(self)
        self.host = host
        self.port = port
        self.keepconnect = keepconnect
        self.protocal = TcpProtocal(host, port, timeout=timeout)
        self.servers = servers
        self.timeout = timeout
        if len(self.servers) == 0 and self.host != '' and self.port != 0:
            self.servers = [ host+':'+str(port) ]
        for server in self.servers:
            host, port = server.split(':')
            self.serversProtocalMap[ server ] = TcpProtocal(host, int(port), timeout = timeout)

    @retryTimes(retryTimes=3)
    def call(self, func, args = ()):
        try:
            self.beforeCall()
            args = self.protocal.tranArgs(args)
            self.protocal.transport.connect()
            package = {
                'func' : func,
                'args' : args,
            }
            msg = self.protocal.serialize(package)
            self.protocal.transport.send(msg)
            respmsg = self.protocal.transport.recv()
            resp = self.protocal.unserialize(respmsg)
            if isinstance(resp, Exception):
                if not self.keepconnect: self.protocal.transport.close()
                raise resp
            if not self.keepconnect: self.protocal.transport.close()
            return resp
        except socket.timeout as ex:
            self.protocal.transport.close()
            raise ex

    def getProtocalInstance(self, instance):
        key = "%s:%s:%s" % (instance.service, instance.address, instance.port)
        if key in self.protocalMap:
            return self.protocalMap.get(key)
        self.protocalMap[key] =  TcpProtocal(instance.address, instance.port)
        return self.protocalMap[key]


class UdpRpcClient(RpcClient):

    def __init__(self, host = '', port = 0, servers=[], timeout = 10):
        RpcClient.__init__(self)
        self.host = host
        self.port = port
        self.protocal = ClientUdpProtocal(host, port, timeout=timeout)
        self.servers = servers
        self.timeout = timeout
        if len(self.servers) == 0 and self.host != '' and self.port != 0:
            self.servers = [ host+':'+str(port) ]
        for server in self.servers:
            host, port = server.split(':')
            self.serversProtocalMap[ server ] = ClientUdpProtocal(host, int(port), timeout=timeout)

    @retryTimes(retryTimes=3)
    def call(self, func, args = ()):
        try:
            self.beforeCall()
            args = self.protocal.tranArgs(args)
            package = {
                'func' : func,
                'args' : args,
            }
            msg = self.protocal.serialize(package)
            self.protocal.transport.send(msg)
            respmsg, _ = self.protocal.transport.recv()
            resp = self.protocal.unserialize(respmsg)
            if isinstance(resp, Exception):
                raise resp
            return resp
        except socket.timeout as ex:
            self.protocal.newTransport()
            raise ex

    def getProtocalInstance(self, instance):
        key = "%s:%s:%s" % (instance.service, instance.address, instance.port)
        if key in self.protocalMap:
            return self.protocalMap.get(key)
        self.protocalMap[key] =  UdpProtocal(instance.address, instance.port)
        return self.protocalMap[key]


class HttpRpcClient(RpcClient):

    def __init__(self, host = '', port = 0, servers = [], timeout = 10):
        RpcClient.__init__(self)
        self.host = host
        self.port = port
        self.protocal = HttpProtocal(host, port, timeout=timeout)
        self.servers = servers
        self.timeout = timeout
        if len(self.servers) == 0 and self.host != '' and self.port != 0:
            self.servers = [ host+':'+str(port) ]
        for server in self.servers:
            host, port = server.split(':')
            self.serversProtocalMap[ server ] = HttpProtocal(host, int(port), timeout=timeout)

    @retryTimes(retryTimes=3)
    def call(self, func, args = ()):
        self.beforeCall()
        args = self.protocal.tranArgs(args)
        package = {
            'func' : func,
            'args' : args,
        }
        msg = self.protocal.serialize(package)
        respmsg = self.protocal.transport.send(msg)
        resp = self.protocal.unserialize(respmsg)
        if isinstance(resp, FuncNotFoundException):
            raise resp
        return resp

    def getProtocalInstance(self, instance):
        key = "%s:%s:%s" % (instance.service, instance.address, instance.port)
        if key in self.protocalMap:
            return self.protocalMap.get(key)
        self.protocalMap[key] =  HttpProtocal(instance.address, instance.port)
        return self.protocalMap[key]