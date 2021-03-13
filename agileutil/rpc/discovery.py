#coding=utf-8

from agileutil.consul import ConsulApi, Instance
import time
import threading


class RpcDiscovery(object):
    pass


class DiscoveryConfig(object):

    def __init__(self, consulHost, consulPort, serviceName, serviceHost = '', servicePort = 0):
        self.consulHost = consulHost
        self.consulPort = consulPort
        self.serviceName = serviceName
        self.serviceHost = serviceHost
        self.servicePort = servicePort


class ConsulRpcDiscovery(RpcDiscovery):

    def __init__(self, consulHost, consulPort):
        self.consulHost = consulHost
        self.consulPort = consulPort
        self.consulApi = ConsulApi(consulHost, consulPort)
        self.instanceList = []
        self.heartbeatInterval = 10

    def doHeartbeat(self, service, address, port, interval):
        while 1:
            try:
                self.consulApi.ttlHeartbeat(service, address, port)
            except:
                pass
            time.sleep(interval)

    def regist(self, service, address, port, ttlHeartBeat = True):
        self.consulApi.registService(serviceName = service, address = address, port=port)
        if ttlHeartBeat:
            t = threading.Thread(target=self.doHeartbeat, args=(service, address, port, self.heartbeatInterval))
            t.start()

    def getInstanceList(self, service):
        instanceList = self.consulApi.getServiceInstanceList(service)
        return instanceList