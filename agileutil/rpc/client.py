#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal, UdpProtocal
from agileutil.rpc.exception import FuncNotFoundException
from agileutil.rpc.discovery import DiscoveryConfig
from agileutil.rpc.discovery import ConsulRpcDiscovery
from agileutil.wrap import retry, retryTimes

class RpcClient(object): 

    def __init__(self):
        self.discoveryConfig = None
        self.discovery = None

    def setDiscoveryConfig(self, config: DiscoveryConfig):
        self.discoveryConfig = config
        self.discovery = ConsulRpcDiscovery(self.discoveryConfig.consulHost, self.discoveryConfig.consulPort)
        

class TcpRpcClient(RpcClient):

    def __init__(self, host, port, keepconnect = True):
        self.host = host
        self.port = port
        self.keepconnect = keepconnect
        self.protocal = TcpProtocal(host, port)

    @retryTimes(retryTimes=3)
    def call(self, func, args = ()):
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

    def close(self):
        self.protocal.transport.close()

class DisconfTcpRpcClient(TcpRpcClient):

    def __init__(self, discoveryConfig:DiscoveryConfig):
        TcpRpcClient.__init__(self, host='', port=0)
        self.setDiscoveryConfig(discoveryConfig)
        self.instanceIndex = 0
        self.protocalMap = {}
        self.isSync = False
        self.syncInterval = 30

    def getInstance(self):
        instanceList = self.discovery.getInstanceList(self.discoveryConfig.serviceName)
        instanceLength  = len(instanceList)
        if instanceLength == 0:
            raise Exception('no instance found')
        index = self.instanceIndex % instanceLength
        self.instanceIndex = self.instanceIndex + 1
        return instanceList[index]

    def getProtocalInstance(self, instance):
        key = "%s:%s:%s" % (instance.service, instance.address, instance.port)
        if key in self.protocalMap:
            return self.protocalMap.get(key)
        self.protocalMap[key] =  TcpProtocal(instance.address, instance.port)
        return self.protocalMap[key]

    def refreshProtocal(self):
        instance = self.getInstance()
        self.protocal = self.getProtocalInstance(instance)

    @retryTimes(retryTimes=3)
    def call(self, func, args = ()):
        self.refreshProtocal()
        return super().call(func, args)
        


class UdpRpcClient(RpcClient):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.protocal = UdpProtocal(host, port)

    @retryTimes(retryTimes=3)
    def call(self, func, args):
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