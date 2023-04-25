import hashlib
import ujson
from sunyata.util import local_ip
from dataclasses import dataclass
import aiohttp


@dataclass
class Instance(object):
    service: str
    address: str
    port: int


class ConsulApi(object):

    __slots__ = ('host', 'port', 'baseUrl', 'token', 'timeout', 'headers')

    def __init__(self, host: str, port: int, token = ''):
        self.host = host
        self.port = port
        self.baseUrl = 'http://%s:%s' % (self.host, self.port)
        self.token = token
        self.timeout = 5
        self.headers = {}
        if self.token:
            self.headers = {'X-Consul-Token':self.token}

    async def getInstanceMap(self):
        async with aiohttp.ClientSession() as sess:
            url = self.baseUrl + '/v1/agent/services'
            async with sess.get(url, headers=self.headers, timeout = self.timeout) as r:
                text = await r.text()
                if r.status != 200:
                    raise Exception(text)
                return ujson.loads(text)

    def genInstanceID(self, service: str, host: str, port: int):
        key = "%s:%s:%s" % (service, host, port)
        m = hashlib.md5()
        m.update(key.encode())
        return m.hexdigest()

    async def registService(self, serviceName: str, port = 80, address=None, ttl=30, degisterAfter = '1m'):
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
        async with aiohttp.ClientSession() as sess:
            url = self.baseUrl + '/v1/agent/service/register'
            async with sess.put(url, headers = self.headers, data=ujson.dumps(params), timeout = self.timeout) as r:
                text = await r.text()
                print('[consul] regist ', text, r.status)

    async def get(self, k: str):
        async with aiohttp.ClientSession() as sess:
            url = self.baseUrl + '/v1/kv/%s?raw=true' % k  
            async with sess.get(url, headers=self.headers, timeout = self.timeout) as r:
                if r.status_code != 200:
                    raise Exception(r.text)
                return r.text

    async def getServiceInstanceList(self, serviceName: str) -> list:
        instanceMap = await self.getInstanceMap()
        instanceList = []
        for instanceID, info in instanceMap.items():
            if info.get('Service') == serviceName:
                instance = Instance(
                    service = serviceName,
                    address = info.get('Address'),
                    port = int(info.get('Port'))
                )
                instanceList.append(instance)
        return instanceList

    async def ttlHeartbeat(self, service, address, port):
        async with aiohttp.ClientSession() as sess:
            url = self.baseUrl + '/v1/agent/check/pass/%s' % ('service:' + self.genInstanceID(service, address, port))
            async with sess.put(url, headers=self.headers, timeout = self.timeout) as r:
                if r.status_code != 200:
                    raise Exception(r.text)