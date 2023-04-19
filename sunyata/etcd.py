import ujson
import requests
from sunyata.util import local_ip
from sunyata.consul import Instance


class EtcdApi(object):

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.baseUrl = 'http://%s:%s' % (self.host, self.port)
        self.timeout = 5
        self.headers = {}

    def registService(self, serviceName: str, port = 80, address=None, ttl=30):
        url = self.baseUrl + '/v2/keys/sunyata-services/%s?dir=true&ttl=%s' % (serviceName, ttl)
        r = requests.put(url, timeout=self.timeout, headers=self.headers)
        if address:
            key  = address + ':' + str(port)
        else:
            key = local_ip() + ':' + str(port)
        val = key
        url = self.baseUrl + '/v2/keys/sunyata-services/%s/%s?value=%s&ttl=%s' % (serviceName, key, val, ttl)
        r = requests.put(url, timeout=self.timeout, headers=self.headers)
        print(r.text, r.status_code)

    def getServiceInstanceList(self, serviceName: str) -> list:
        url = self.baseUrl + '/v2/keys/sunyata-services/%s' % serviceName
        r = requests.get(url, timeout=self.timeout, headers=self.headers)
        dic = ujson.loads(r.text)
        print(r.status_code, r.text)
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
    
    def ttlHeartbeat(self, service, address, port):
        self.registService(serviceName=service, address=address, port=port)