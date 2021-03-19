#coding=utf-8

import threading
import time
import unittest
from multiprocessing import Process


def sayHello(name): return 'hello ' + name


class TestRpcServerClient(unittest.TestCase):

    def test_tcp_server_client(self):
        '''测试TCP'''
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

        tServer = threading.Thread(target=create_server, args=())
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client, args=())
        tClient.start()

    def test_udp_server_client(self):
        '''测试UDP'''
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
        
        tServer = threading.Thread(target=create_server, args=())
        tServer.start()
        time.sleep(1)
        tClient = threading.Thread(target=create_client, args=())
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

if __name__ == '__main__':
    #测试HTTP
    tServer = Process(target=create_http_server, args=())
    tServer.start()
    time.sleep(3)
    tClient = threading.Thread(target=create_http_client, args=())
    tClient.start()
    time.sleep(3)
    tServer.terminate()
    tServer.join()
    #测试其他
    unittest.main()