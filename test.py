#coding=utf-8

import threading
import time
import unittest
from multiprocessing import Process
from agileutil.util import local_ip

CONSUL_HOST = '192.168.19.103'
CONSUL_PORT = 8500


def sayHello(name): return 'hello ' + name

class A(object):
    def __init__(self, val):
        self.val = val
    def dump(self):
        print('self.val', self.val)


class TestRpcServerClient(unittest.TestCase):

    def test_tcp_server_client(self):
        #测试TCP
        def create_server():
            from agileutil.rpc.server import TcpRpcServer
            server = TcpRpcServer('127.0.0.1', 9988)
            server.regist(sayHello)
            server.serve()

        def create_client():
            from agileutil.rpc.client import TcpRpcClient
            client = TcpRpcClient('127.0.0.1', 9988)
            for i in range(3):
                resp = client.call(func='sayHello', args=('zhangsan'))
                self.assertEqual(resp, 'hello zhangsan')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_udp_server_client(self):
        #测试UDP
        def create_server():
            from agileutil.rpc.server import UdpRpcServer
            server = UdpRpcServer('127.0.0.1', 9999)
            server.regist(sayHello)
            server.serve()

        def create_client():
            from agileutil.rpc.client import UdpRpcClient
            client = UdpRpcClient('127.0.0.1', 9999)
            for i in range(3):
                resp = client.call(func='sayHello', args=('lisi'))
                self.assertEqual(resp, 'hello lisi')
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_tcp_server_discovery(self):
        #测试TCP服务发现
        def create_server():
            from agileutil.rpc.server import TcpRpcServer
            from agileutil.rpc.discovery import DiscoveryConfig
            disconf = DiscoveryConfig(
                consulHost = CONSUL_HOST,
                consulPort = CONSUL_PORT,
                serviceName = 'test-rpc-server',
                serviceHost = local_ip(),
                servicePort = 10001
            )
            server = TcpRpcServer('0.0.0.0', 10001)
            server.setDiscoverConfig(disconf)
            server.regist(sayHello)
            server.serve()

        def create_client():
            from agileutil.rpc.client import TcpRpcClient
            from agileutil.rpc.discovery import DiscoveryConfig
            cli = TcpRpcClient()
            disconf = DiscoveryConfig(
                consulHost= CONSUL_HOST,
                consulPort= CONSUL_PORT,
                serviceName='test-rpc-server'
            )
            cli.setDiscoveryConfig(disconf)
            for i in range(3):
                resp = cli.call(func = 'sayHello', args=('mary'))
                self.assertEqual(resp, 'hello mary')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()      
    
    def test_udp_server_discovery(self):  
        #测试UDP服务发现
        def create_server():
            from agileutil.rpc.server import UdpRpcServer
            from agileutil.rpc.discovery import DiscoveryConfig
            disconf = DiscoveryConfig(
                consulHost = CONSUL_HOST,
                consulPort = CONSUL_PORT,
                serviceName = 'test-udp-rpc-server',
                serviceHost = local_ip(),
                servicePort = 10002
            )
            server = UdpRpcServer('0.0.0.0', 10002)
            server.setDiscoverConfig(disconf)
            server.regist(sayHello)
            server.serve()

        def create_client():
            from agileutil.rpc.client import UdpRpcClient
            from agileutil.rpc.discovery import DiscoveryConfig
            client = UdpRpcClient()
            disconf = DiscoveryConfig(
                consulHost= CONSUL_HOST,
                consulPort= CONSUL_PORT,
                serviceName='test-udp-rpc-server'
            )
            client.setDiscoveryConfig(disconf)
            for i in range(3):
                resp = client.call(func = 'sayHello', args=('mary'))
                self.assertEqual(resp, 'hello mary')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(3)
        tClient = threading.Thread(target=create_client)
        tClient.start()  

    def test_serialize_obj(self):
        #测试TCP
        def create_server():
            from agileutil.rpc.server import TcpRpcServer
            def retObj():
                return A(10)
            server = TcpRpcServer('127.0.0.1', 10004)
            server.regist(retObj)
            server.serve()

        def create_client():
            from agileutil.rpc.client import TcpRpcClient
            client = TcpRpcClient('127.0.0.1', 10004)
            for i in range(3):
                resp = client.call(func='retObj')
                #print("resp.val", resp.val)
                #resp.dump()
                self.assertEqual(resp.val, 10)

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_multi_server(self):
        def create_server_10005():
            from agileutil.rpc.server import TcpRpcServer
            server = TcpRpcServer('127.0.0.1', 10005)
            server.regist(sayHello)
            server.serve()
        def create_server_10006():
            from agileutil.rpc.server import TcpRpcServer
            server = TcpRpcServer('127.0.0.1', 10006)
            server.regist(sayHello)
            server.serve()
        def create_server_10007():
            from agileutil.rpc.server import TcpRpcServer
            server = TcpRpcServer('127.0.0.1', 10007)
            server.regist(sayHello)
            server.serve()
        def create_client():
            from agileutil.rpc.client import TcpRpcClient
            client = TcpRpcClient(servers=[  
                '127.0.0.1:10005',
                '127.0.0.1:10006',
                '127.0.0.1:10007',
                '127.0.0.1:10008',
            ])
            for i in range(10):
                resp = client.call(func='sayHello', args=('zhangsan'))
                print('tcp server', client.debugGetLastServer())
                self.assertEqual(resp, 'hello zhangsan')
        tServer_10005 = threading.Thread(target=create_server_10005)
        tServer_10006 = threading.Thread(target=create_server_10006)
        tServer_10007 = threading.Thread(target=create_server_10007)
        tServer_10005.start()
        tServer_10006.start()
        tServer_10007.start()
        time.sleep(3)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_multi_udp_server_client(self):
        #测试UDP
        def create_server_10008():
            from agileutil.rpc.server import UdpRpcServer
            server = UdpRpcServer('127.0.0.1', 10008)
            server.regist(sayHello)
            server.serve()
        def create_server_10009():
            from agileutil.rpc.server import UdpRpcServer
            server = UdpRpcServer('127.0.0.1', 10009)
            server.regist(sayHello)
            server.serve()
        def create_server_10010():
            from agileutil.rpc.server import UdpRpcServer
            server = UdpRpcServer('127.0.0.1', 10010)
            server.regist(sayHello)
            server.serve()
        def create_client():
            from agileutil.rpc.client import UdpRpcClient
            client = UdpRpcClient(servers = [
                '127.0.0.1:10008',
                '127.0.0.1:10009',
                '127.0.0.1:10010',
            ])
            for i in range(10):
                resp = client.call(func='sayHello', args=('lisi'))
                print('udp server:', client.lastServer)
                self.assertEqual(resp, 'hello lisi')
        tServer_10008 = threading.Thread(target=create_server_10008)
        tServer_10009 = threading.Thread(target=create_server_10009)
        tServer_10010 = threading.Thread(target=create_server_10010)
        tServer_10008.start()
        tServer_10009.start()
        tServer_10010.start()
        time.sleep(3)
        tClient = threading.Thread(target=create_client)
        tClient.start()

def create_http_server():
    from agileutil.rpc.server import HttpRpcServer
    server = HttpRpcServer('127.0.0.1', 10000)
    server.regist(sayHello)
    server.serve()

def create_http_client():
    from agileutil.rpc.client import HttpRpcClient
    client = HttpRpcClient('127.0.0.1', 10000)
    for i in range(3):
        resp = client.call(func = 'sayHello', args = ('xiaoming'))
        assert (resp == 'hello xiaoming')

def create_http_server_discovery():
    from agileutil.rpc.server import HttpRpcServer
    from agileutil.rpc.discovery import DiscoveryConfig
    server = HttpRpcServer('127.0.0.1', 10003)
    disconf = DiscoveryConfig(
        consulHost = CONSUL_HOST,
        consulPort = CONSUL_PORT,
        serviceName = 'test-http-rpc-server',
        serviceHost = local_ip(),
        servicePort = 10003,
    )
    server.setDiscoverConfig(disconf)
    server.regist(sayHello)
    server.serve()

def create_http_client_discovery():
    from agileutil.rpc.client import HttpRpcClient
    from agileutil.rpc.discovery import DiscoveryConfig
    client = HttpRpcClient()
    disconf = DiscoveryConfig(
        consulHost = CONSUL_HOST,
        consulPort = CONSUL_PORT,
        serviceName = 'test-http-rpc-server',
    )
    client.setDiscoveryConfig(disconf)
    for i in range(3):
        resp = client.call('sayHello', ('xiaoming'))
        assert (resp == 'hello xiaoming')

def create_http_server_10011():
    from agileutil.rpc.server import HttpRpcServer
    server = HttpRpcServer('127.0.0.1', 10011)
    server.regist(sayHello)
    server.serve()

def create_http_server_10012():
    from agileutil.rpc.server import HttpRpcServer
    server = HttpRpcServer('127.0.0.1', 10012)
    server.regist(sayHello)
    server.serve()

def create_http_server_10013():
    from agileutil.rpc.server import HttpRpcServer
    server = HttpRpcServer('127.0.0.1', 10013)
    server.regist(sayHello)
    server.serve()

def create_http_client_multi():
    from agileutil.rpc.client import HttpRpcClient
    client = HttpRpcClient(servers = [
        '127.0.0.1:10011',
        '127.0.0.1:10012',
        '127.0.0.1:10013'
    ])
    for i in range(10):
        resp = client.call(func = 'sayHello', args = ('xiaoming'))
        print('http server', client.debugGetLastServer())
        assert (resp == 'hello xiaoming')

if __name__ == '__main__':
    #测试HTTP
    tServer = Process(target=create_http_server)
    tServer.start()
    time.sleep(3)
    tClient = threading.Thread(target=create_http_client)
    tClient.start()
    time.sleep(1)
    tServer.terminate()
    tServer.join()
    #测试HTTP服务发现
    httpServer = Process(target=create_http_server_discovery)
    httpServer.start()
    time.sleep(3)
    httpClient = threading.Thread(target=create_http_client_discovery)
    httpClient.start()
    #测试HTTP多个服务端地址
    httpServer_10011 = Process(target=create_http_server_10011)
    httpServer_10012 = Process(target=create_http_server_10012)
    httpServer_10013 = Process(target=create_http_server_10013)
    httpServer_10011.start()
    httpServer_10012.start()
    httpServer_10013.start()
    time.sleep(3)
    httpClient_multi = threading.Thread(target=create_http_client_multi)
    httpClient_multi.start()
    #测试其他
    unittest.main()