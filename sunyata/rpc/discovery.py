from sunyata.consul import ConsulApi, Instance
import time
import threading
import asyncio
from sunyata.etcd import EtcdApi


class DiscoveryConfig(object):

    def __init__(self, serviceName, consulHost = None, consulPort = None, etcdHost=None, etcdPort=None, serviceHost = '', servicePort = 0, consulToken=''):
        self.consulHost = consulHost
        self.consulPort = consulPort
        self.consulToken = consulToken
        self.serviceName = serviceName
        self.serviceHost = serviceHost
        self.servicePort = servicePort
        self.etcdHost = etcdHost
        self.etcdPort = etcdPort


class RpcDiscovery(object):

    def __init__(self, consulHost=None, consulPort=None, consulToken='', etcdHost=None, etcdPort=None):
        self.consulHost = consulHost
        self.consulPort = consulPort
        self.consulToken = consulToken
        self.etcdHost = etcdHost
        self.etcdPort = etcdPort
        self.api = None
        if self.consulHost and self.consulPort:
            self.api = ConsulApi(consulHost, consulPort, consulToken)
        if self.etcdHost and self.etcdPort:
            self.api = EtcdApi(etcdHost, etcdPort)
        self.instanceList = []
        self.heartbeatInterval = 15

    #def doHeartbeat(self, service, address, port, interval):
    #    while 1:
    #        try:
    #            self.api.ttlHeartbeat(service, address, port)
    #        except:
    #            pass
    #        time.sleep(interval)
    
    async def asyncDoHeartbeat(self, service, address, port, interval):
        while 1:
            try:
                await self.api.ttlHeartbeat(service, address, port)
            except:
                pass
            await asyncio.sleep(interval)

    #def regist(self, service, address, port, ttlHeartBeat = True):
    #    self.api.registService(serviceName = service, address = address, port=port)
    #    if ttlHeartBeat:
    #        t = threading.Thread(target=self.doHeartbeat, args=(service, address, port, self.heartbeatInterval))
    #        t.setDaemon(True)
    #        t.start()

    async def asyncRegist(self, service, address, port, ttlHeartBeat = True):
        await self.api.registService(serviceName = service, address = address, port=port)
        await self.asyncDoHeartbeat(service, address, port, self.heartbeatInterval)

    async def getInstanceList(self, service):
        instanceList = await self.api.getServiceInstanceList(service)
        return instanceList