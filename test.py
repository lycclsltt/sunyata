"""
单元测试脚本:

python3 -W ignore test.py
"""

import threading
import time
import unittest
from multiprocessing import Process
from agileutil.util import local_ip
import socket
import requests
import agileutil.rpc.const
from sanic.log import logger
import logging
import random
from agileutil.rpc.compress import RpcCompress
from agileutil.rpc.server import TcpRpcServer
from agileutil.rpc.client import TcpRpcClient
from agileutil.rpc.server import UdpRpcServer
from agileutil.rpc.client import UdpRpcClient
from agileutil.rpc.discovery import DiscoveryConfig
from agileutil.rpc.compress import RpcCompress
from agileutil.rpc.server import HttpRpcServer
from agileutil.rpc.client import HttpRpcClient
from agileutil.rpc.server import RpcServer
from agileutil.rpc import rpc

CONSUL_HOST = '192.168.19.103'
CONSUL_PORT = 8500
SLEEP = 1

RpcServer.isPrintLogo = False


@rpc
class TestService(object):
    def add(self, n1, n2):
        return n1 + n2


def sayHello(name): return 'hello ' + name

def testTimeout():
    time.sleep(3)
    return 'finish'

class A(object):
    def __init__(self, val):
        self.val = val
    def dump(self):
        print('self.val', self.val)


class TestRpcServerClient(unittest.TestCase):

    def test_tcp_server_client(self):
        #测试TCP
        def create_server():
            server = TcpRpcServer('127.0.0.1', 9988)
            server.regist(sayHello)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 9988)
            for i in range(3):
                resp = client.call('sayHello', 'zhangsan')
                self.assertEqual(resp, 'hello zhangsan')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_udp_server_client(self):
        #测试UDP
        def create_server():
            server = UdpRpcServer('127.0.0.1', 9999)
            server.regist(sayHello)
            server.serve()

        def create_client():
            client = UdpRpcClient('127.0.0.1', 9999)
            for i in range(3):
                resp = client.call('sayHello', 'lisi' )
                self.assertEqual(resp, 'hello lisi')
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_tcp_server_discovery(self):
        if socket.gethostname() == 'ubuntu': return
        #测试TCP服务发现
        def create_server():
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
            cli = TcpRpcClient()
            disconf = DiscoveryConfig(
                consulHost= CONSUL_HOST,
                consulPort= CONSUL_PORT,
                serviceName='test-rpc-server'
            )
            cli.setDiscoveryConfig(disconf)
            for i in range(3):
                resp = cli.call('sayHello', 'mary')
                self.assertEqual(resp, 'hello mary')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()      
    
    def test_udp_server_discovery(self): 
        if socket.gethostname() == 'ubuntu': return 
        #测试UDP服务发现
        def create_server():
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
            client = UdpRpcClient()
            disconf = DiscoveryConfig(
                consulHost= CONSUL_HOST,
                consulPort= CONSUL_PORT,
                serviceName='test-udp-rpc-server'
            )
            client.setDiscoveryConfig(disconf)
            for i in range(3):
                resp = client.call('sayHello', 'mary')
                self.assertEqual(resp, 'hello mary')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()  

    def test_serialize_obj(self):
        #测试TCP
        def create_server():
            def retObj():
                return A(10)
            server = TcpRpcServer('127.0.0.1', 10004)
            server.regist(retObj)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 10004)
            for i in range(3):
                resp = client.call('retObj')
                self.assertEqual(resp.val, 10)

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_multi_server(self):
        def create_server_10005():
            server = TcpRpcServer('127.0.0.1', 10005)
            server.regist(sayHello)
            server.serve()
        def create_server_10006():
            server = TcpRpcServer('127.0.0.1', 10006)
            server.regist(sayHello)
            server.serve()
        def create_server_10007():
            server = TcpRpcServer('127.0.0.1', 10007)
            server.regist(sayHello)
            server.serve()
        def create_client():
            client = TcpRpcClient(servers=[  
                '127.0.0.1:10005',
                '127.0.0.1:10006',
                '127.0.0.1:10007',
            ])
            for i in range(10):
                resp = client.call('sayHello', 'zhangsan')
                self.assertEqual(resp, 'hello zhangsan')
        tServer_10005 = threading.Thread(target=create_server_10005)
        tServer_10006 = threading.Thread(target=create_server_10006)
        tServer_10007 = threading.Thread(target=create_server_10007)
        tServer_10005.start()
        tServer_10006.start()
        tServer_10007.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_multi_udp_server_client(self):
        #测试UDP
        def create_server_10008():
            server = UdpRpcServer('127.0.0.1', 10008)
            server.regist(sayHello)
            server.serve()
        def create_server_10009():
            server = UdpRpcServer('127.0.0.1', 10009)
            server.regist(sayHello)
            server.serve()
        def create_server_10010():
            server = UdpRpcServer('127.0.0.1', 10010)
            server.regist(sayHello)
            server.serve()
        def create_client():
            client = UdpRpcClient(servers = [
                '127.0.0.1:10008',
                '127.0.0.1:10009',
                '127.0.0.1:10010',
            ])
            for i in range(10):
                resp = client.call('sayHello', 'lisi')
                self.assertEqual(resp, 'hello lisi')
        tServer_10008 = threading.Thread(target=create_server_10008)
        tServer_10009 = threading.Thread(target=create_server_10009)
        tServer_10010 = threading.Thread(target=create_server_10010)
        tServer_10008.start()
        tServer_10009.start()
        tServer_10010.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_tcp_server_client_timeout(self):
        #测试TCP
        def create_server():
            server = TcpRpcServer('127.0.0.1', 10014)
            server.regist(testTimeout)
            server.regist(sayHello)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 10014, timeout = 2)
            tag = ''
            try:
                resp = client.call('testTimeout')
                self.assertEqual(resp, 'finish')
            except socket.timeout as ex:
                tag = 'test timeout ok!'
            self.assertEqual(tag, 'test timeout ok!')
            resp = client.call('sayHello', 'xiaoming')
            self.assertEqual(resp, 'hello xiaoming')
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()
    
    def test_udp_server_client_timeout(self):
        #测试UDP
        def create_server():
            server = UdpRpcServer('127.0.0.1', 10015)
            server.regist(sayHello)
            server.regist(testTimeout)
            server.serve()

        def create_client():
            client = UdpRpcClient('127.0.0.1', 10015, timeout=2)
            tag = ''
            try:
                resp = client.call('testTimeout')
            except socket.timeout as ex:
                tag = 'udp timeout'
            self.assertEqual(tag, 'udp timeout')
            resp = client.call('sayHello', 'xiaoming')
            time.sleep(5)
            self.assertEqual(resp, 'hello xiaoming')

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_tcp_server_server_timeout(self):
        #测试TCP
        def create_server():
            server = TcpRpcServer('127.0.0.1', 10017)
            server.regist(sayHello)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 10017, timeout = 2)
            resp = client.call('sayHello', 'xiaoming')
            self.assertEqual(resp, 'hello xiaoming')
            time.sleep(10)
            resp = client.call('sayHello', 'zhangsan')
            self.assertEqual(resp, 'hello zhangsan')
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_tcp_decorator(self):
        #测试TCP
        def create_server():
            @rpc
            def add(n1, n2):
                return n1 +n2
            server = TcpRpcServer('127.0.0.1', 10018)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 10018, timeout = 2)
            resp = client.call('add', n1=1, n2=1)
            self.assertEqual(resp, 2)
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_tcp_compress(self):
        #测试TCP
        def create_server():
            RpcCompress.DEBUG = True
            RpcCompress.enableCompressLen = 200
            server = TcpRpcServer('127.0.0.1', 10019)
            server.regist(sayHello)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 10019, timeout = 2)
            name = ''.join([ random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(2000) ])
            resp = client.call('sayHello', name)
            self.assertEqual(resp, 'hello ' + name)
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()
    
    def test_udp_compress(self):
        #测试UDP
        def create_server():
            RpcCompress.DEBUG = True
            RpcCompress.enableCompressLen = 200
            server = UdpRpcServer('127.0.0.1', 10020)
            server.regist(sayHello)
            server.serve()

        def create_client():
            client = UdpRpcClient('127.0.0.1', 10020, timeout=2)
            name = ''.join([ random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(2000) ])
            resp = client.call('sayHello', name )
            self.assertEqual(resp, 'hello ' + name)

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(SLEEP)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_regist_class(self):
        def create_server():
            server = TcpRpcServer('127.0.0.1', 10022)
            server.regist(TestService)
            server.serve()

        def create_client():
            client = TcpRpcClient('127.0.0.1', 10022, timeout = 2)
            resp = client.call('TestService.add', n1=1,n2=2)
            self.assertEqual(resp, 3)
        
        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client)
        tClient.start()

    def test_msg_pack_serialize(self):
        from agileutil.rpc.serialize import MsgpackSerialize
        arr = [1,2,3,4,5]
        bytearr = MsgpackSerialize.serialize(arr)
        newarr = MsgpackSerialize.unserialize(bytearr)
        self.assertEqual(arr, newarr)
        print('arr', arr, 'newarr', newarr)


def create_http_server():
    server = HttpRpcServer('127.0.0.1', 10000)
    server.disableLog()
    server.regist(sayHello)
    server.serve()

def create_http_client():
    client = HttpRpcClient('127.0.0.1', 10000)
    for i in range(3):
        resp = client.call('sayHello', 'xiaoming')
        assert (resp == 'hello xiaoming')

def create_http_server_discovery():
    if socket.gethostname() == 'ubuntu': return
    server = HttpRpcServer('127.0.0.1', 10003)
    server.disableLog()
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
    if socket.gethostname() == 'ubuntu': return
    client = HttpRpcClient()
    disconf = DiscoveryConfig(
        consulHost = CONSUL_HOST,
        consulPort = CONSUL_PORT,
        serviceName = 'test-http-rpc-server',
    )
    client.setDiscoveryConfig(disconf)
    for i in range(3):
        resp = client.call('sayHello', 'xiaoming')
        assert (resp == 'hello xiaoming')

def create_http_server_10011():
    server = HttpRpcServer('127.0.0.1', 10011)
    server.disableLog()
    server.regist(sayHello)
    server.serve()

def create_http_server_10012():
    server = HttpRpcServer('127.0.0.1', 10012)
    server.disableLog()
    server.regist(sayHello)
    server.serve()

def create_http_server_10013():
    server = HttpRpcServer('127.0.0.1', 10013)
    server.disableLog()
    server.regist(sayHello)
    server.serve()

def create_http_client_multi():
    client = HttpRpcClient(servers = [
        '127.0.0.1:10011',
        '127.0.0.1:10012',
        '127.0.0.1:10013'
    ])
    for i in range(10):
        resp = client.call('sayHello', 'xiaoming')
        assert (resp == 'hello xiaoming')

def create_http_server_timeout():
    server = HttpRpcServer('127.0.0.1', 10016)
    server.disableLog()
    server.regist(testTimeout)
    server.regist(sayHello)
    server.serve()

def create_http_client_timeout():
    client = HttpRpcClient('127.0.0.1', 10016, timeout=2)
    tag = ''
    try:
        resp = client.call('testTimeout')
    except requests.exceptions.ReadTimeout as ex:
        tag = 'http timeout'
    assert(  tag == 'http timeout')
    resp = client.call('sayHello', 'xiaoming')
    assert( resp == 'hello xiaoming' )

def create_http_server_compress():
    RpcCompress.DEBUG = True
    RpcCompress.enableCompressLen = 200
    server = HttpRpcServer('127.0.0.1', 10021)
    server.disableLog()
    server.regist(sayHello)
    server.serve()

def create_http_client_compress():
    RpcCompress.DEBUG = True
    client = HttpRpcClient('127.0.0.1', 10021, timeout=2)
    name = ''.join([ random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(2000) ])
    resp = client.call('sayHello', name)
    assert( resp == 'hello ' + name )

if __name__ == '__main__':
    #测试HTTP
    tServer = Process(target=create_http_server)
    tServer.start()
    time.sleep(SLEEP)
    tClient = threading.Thread(target=create_http_client)
    tClient.start()
    time.sleep(SLEEP)
    tServer.terminate()
    tServer.join()
    #测试HTTP服务发现
    httpServer = Process(target=create_http_server_discovery)
    httpServer.start()
    time.sleep(SLEEP)
    httpClient = threading.Thread(target=create_http_client_discovery)
    httpClient.start()
    #测试HTTP多个服务端地址
    httpServer_10011 = Process(target=create_http_server_10011)
    httpServer_10012 = Process(target=create_http_server_10012)
    httpServer_10013 = Process(target=create_http_server_10013)
    httpServer_10011.start()
    httpServer_10012.start()
    httpServer_10013.start()
    time.sleep(SLEEP)
    httpClient_multi = threading.Thread(target=create_http_client_multi)
    httpClient_multi.start()
    #测试http超时
    httpServer = Process(target=create_http_server_timeout)
    httpServer.start()
    time.sleep(SLEEP)
    httpClient = threading.Thread(target=create_http_client_timeout)
    httpClient.start()
    #测试http压缩
    httpServer = Process(target=create_http_server_compress)
    httpServer.start()
    time.sleep(SLEEP)
    httpClient = threading.Thread(target=create_http_client_compress)
    httpClient.start()
    #测试其他
    unittest.main()