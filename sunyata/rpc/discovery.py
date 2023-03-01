from sunyata.consul import ConsulApi, Instance
import time
import threading
import asyncio


class RpcDiscovery(object):
    pass


class DiscoveryConfig(object):

    __slots__ = ('consulHost', 'consulPort', 'serviceName', 'serviceHost', 'servicePort', 'consulToken')

    def __init__(self, consulHost, consulPort, serviceName, serviceHost = '', servicePort = 0, consulToken=''):
        self.consulHost = consulHost
        self.consulPort = consulPort
        self.consulToken = consulToken
        self.serviceName = serviceName
        self.serviceHost = serviceHost
        self.servicePort = servicePort


class ConsulRpcDiscovery(RpcDiscovery):

    def __init__(self, consulHost, consulPort, consulToken):
        self.consulHost = consulHost
        self.consulPort = consulPort
        self.consulToken = consulToken
        self.consulApi = ConsulApi(consulHost, consulPort, consulToken)
        self.instanceList = []
        self.heartbeatInterval = 10

    def doHeartbeat(self, service, address, port, interval):
        while 1:
            try:
                self.consulApi.ttlHeartbeat(service, address, port)
            except:
                pass
            time.sleep(interval)
    
    async def asyncDoHeartbeat(self, service, address, port, interval):
        while 1:
            try:
                self.consulApi.ttlHeartbeat(service, address, port)
            except:
                pass
            await asyncio.sleep(interval)

    def regist(self, service, address, port, ttlHeartBeat = True):
        self.consulApi.registService(serviceName = service, address = address, port=port)
        if ttlHeartBeat:
            t = threading.Thread(target=self.doHeartbeat, args=(service, address, port, self.heartbeatInterval))
            t.start()

    async def asyncRegist(self, service, address, port, ttlHeartBeat = True):
        self.consulApi.registService(serviceName = service, address = address, port=port)
        await self.asyncDoHeartbeat(service, address, port, self.heartbeatInterval)

    def getInstanceList(self, service):
        instanceList = self.consulApi.getServiceInstanceList(service)
        return instanceList