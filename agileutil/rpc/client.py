#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal, UdpProtocal, HttpProtocal, RpcProtocal
from agileutil.rpc.exception import FuncNotFoundException
from agileutil.rpc.discovery import DiscoveryConfig
from agileutil.rpc.discovery import ConsulRpcDiscovery
from agileutil.wrap import retryTimes

class RpcClient(object): 

    def __init__(self):
        self.discoveryConfig = None
        self.discovery = None
        self.instanceIndex = 0
        self.protocalMap = {}
        self.isSync = False
        self.syncInterval = 30
        self.protocal = RpcProtocal()

    def getInstance(self):
        instanceList = self.discovery.getInstanceList(self.discoveryConfig.serviceName)
        instanceLength  = len(instanceList)
        if instanceLength == 0:
            raise Exception('no instance found')
        index = self.instanceIndex % instanceLength
        self.instanceIndex = self.instanceIndex + 1
        return instanceList[index]

    def refreshProtocal(self):
        instance = self.getInstance()
        self.protocal = self.getProtocalInstance(instance)

    def setDiscoveryConfig(self, config: DiscoveryConfig):
        self.discoveryConfig = config
        self.discovery = ConsulRpcDiscovery(self.discoveryConfig.consulHost, self.discoveryConfig.consulPort)

    def close(self):
        self.protocal.transport.close()
        

class TcpRpcClient(RpcClient):

    def __init__(self, host = '', port = 0, keepconnect = True):
        RpcClient.__init__(self)
        self.host = host
        self.port = port
        self.keepconnect = keepconnect
        self.protocal = TcpProtocal(host, port)

    @retryTimes(retryTimes=3)
    def call(self, func, args = ()):
        if self.discovery:
            self.refreshProtocal()
        if args == None: args = ()
        try:
            self.protocal.transport.connect()
        except Exception as ex:
            pass

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

    def getProtocalInstance(self, instance):
        key = "%s:%s:%s" % (instance.service, instance.address, instance.port)
        if key in self.protocalMap:
            return self.protocalMap.get(key)
        self.protocalMap[key] =  TcpProtocal(instance.address, instance.port)
        return self.protocalMap[key]


class UdpRpcClient(RpcClient):

    def __init__(self, host = '', port = 0):
        RpcClient.__init__(self)
        self.host = host
        self.port = port
        self.protocal = UdpProtocal(host, port)

    @retryTimes(retryTimes=3)
    def call(self, func, args):
        if self.discovery:
            self.refreshProtocal()
        package = {
            'func' : func,
            'args' : args,
        }
        msg = self.protocal.serialize(package)
        self.protocal.transport.send(msg)
        respmsg, _ = self.protocal.transport.recv()
        resp = self.protocal.unserialize(respmsg)
        if isinstance(resp, FuncNotFoundException):
            raise resp
        return resp

    def getProtocalInstance(self, instance):
        key = "%s:%s:%s" % (instance.service, instance.address, instance.port)
        if key in self.protocalMap:
            return self.protocalMap.get(key)
        self.protocalMap[key] =  UdpProtocal(instance.address, instance.port)
        return self.protocalMap[key]


class HttpRpcClient(RpcClient):

    def __init__(self, host = '', port = 0):
        RpcClient.__init__(self)
        self.host = host
        self.port = port
        self.protocal = HttpProtocal(host, port)

    @retryTimes(retryTimes=3)
    def call(self, func, args):
        if self.discovery:
            self.refreshProtocal()
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
