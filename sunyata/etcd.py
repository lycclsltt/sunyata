import ujson
from sunyata.util import local_ip
from sunyata.consul import Instance
import aiohttp

class EtcdApi(object):

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.baseUrl = 'http://%s:%s' % (self.host, self.port)
        self.timeout = 5
        self.headers = {}

    async def registService(self, serviceName: str, port = 80, address=None, ttl=30):
        async with aiohttp.ClientSession() as sess:
            url = self.baseUrl + '/v2/keys/sunyata-services/%s?dir=true&ttl=%s&prevExist=true' % (serviceName, ttl)
            async with sess.put(url, headers=self.headers, timeout=self.timeout) as r:
                text = await r.text()
                print('[etcd] regist dir', text, r.status)
            if address:
                key  = address + ':' + str(port)
            else:
                key = local_ip() + ':' + str(port)
            val = key
            url = self.baseUrl + '/v2/keys/sunyata-services/%s/%s?value=%s&ttl=%s' % (serviceName, key, val, ttl)
            async with sess.put(url, headers=self.headers, timeout=self.timeout) as r:
                text = await r.text()
                print('[etcd] regist key', text, r.status)

    async def getServiceInstanceList(self, serviceName: str) -> list:
        async with aiohttp.ClientSession() as sess:
            url = self.baseUrl + '/v2/keys/sunyata-services/%s' % serviceName
            async with sess.get(url, timeout=self.timeout, headers=self.headers) as r:
                text = await r.text()
                dic = ujson.loads(text)
                nodes = dic.get('node').get('nodes', [])
                instanceList = []
                for node in nodes:
                    value = node.get('value')
                    ip, port = value.split(':')
                    instance = Instance(
                        service=serviceName,
                        address=ip,
                        port=int(port)
                    )
                    instanceList.append(instance)
                return instanceList
    
    async def ttlHeartbeat(self, service, address, port):
        await self.registService(serviceName=service, address=address, port=port)