#coding=utf-8

import hashlib
import json
import requests
from agileutil.util import local_ip
import time


class Instance(object):

    def __init__(self, service, address, port):
        self.service = service
        self.address = address
        self.port = port


class ConsulApi(object):

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.baseUrl = 'http://%s:%s' % (self.host, self.port)
        self.token = None
        self.timeout = 5

    def put(self, k: str, v: str):
        url = self.baseUrl + '/v1/kv/%s' % k        
        r = requests.put(url, data=v, timeout = self.timeout)
        if r.status_code != 200:
            raise Exception(r.text)

    def getInstanceMap(self):
        url = self.baseUrl + '/v1/agent/services'
        r = requests.get(url, timeout = self.timeout)
        if r.status_code != 200:
            raise Exception(r.text)
        #print(r.text)
        return json.loads(r.text)

    def genInstanceID(self, service: str, host: str, port: int):
        key = "%s:%s:%s" % (service, host, port)
        m = hashlib.md5()
        m.update(key.encode())
        return m.hexdigest()

    def registService(self, serviceName: str, port = 80, address=None, ttl=30, degisterAfter = '1m'):
        params = {
            'Name' : serviceName,
            'Port' : port
        }
        if address:
            params['Address'] = address
        else:
            params['Address'] = local_ip()
        params['ID'] = self.genInstanceID(serviceName, params['Address'], port)
        '''
        params['Check'] = {
            'Interval' : "%ss" % checkInterval,
            'DeregisterCriticalServiceAfter' : '1m',
            'Timeout' : '5s',
            'TCP' : "%s:%s" % (params['Address'], port)
        }
        '''
        params['Check'] = {
            'DeregisterCriticalServiceAfter' : degisterAfter,
            'TTL' : '%ss' % ttl,
        }
        #print('params', json.dumps(params))
        url = self.baseUrl + '/v1/agent/service/register'
        r = requests.put(url, data=json.dumps(params), timeout = self.timeout)
        print(r.text, r.status_code)


    def deregistService(self, serviceName: str, port: int, address = None):
        instanceId = self.genInstanceID(serviceName, address, port)
        url = self.baseUrl + '/v1/agent/service/deregister/%s' % instanceId
        r = requests.put(url, timeout = self.timeout)
        if r.status_code != 200:
            raise Exception(r.text)

    def get(self, k: str):
        url = self.baseUrl + '/v1/kv/%s?raw=true' % k  
        r = requests.get(url, timeout = self.timeout)
        if r.status_code != 200:
            raise Exception(r.text)
        return r.text

    def getServiceInstanceList(self, serviceName: str) -> list:
        instanceMap = self.getInstanceMap()
        instanceList = []
        for instanceID, info in instanceMap.items():
            if info.get('Service') == serviceName:
                instance = Instance(
                    service = serviceName,
                    address = info.get('Address'),
                    port = info.get('Port')
                )
                instanceList.append(instance)
        return instanceList

    def ttlHeartbeat(self, service, address, port):
        url = self.baseUrl + '/v1/agent/check/pass/%s' % ('service:' + self.genInstanceID(service, address, port))
        r = requests.put(url, timeout = self.timeout)
        if r.status_code != 200:
            raise Exception(r.text)