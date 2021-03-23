#coding=utf-8

import threading
import time
import unittest
from multiprocessing import Process
from agileutil.util import local_ip

CONSUL_HOST = '192.168.19.103'
CONSUL_PORT = 8500


def sayHello(name): return 'hello ' + name


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
            requestNum = 100000
            begin = time.time()
            for i in range(requestNum):
                resp = client.call(func='sayHello', args=('zhangsan'))
                self.assertEqual(resp, 'hello zhangsan')
            end = time.time()
            cost = end - begin
            print('%s request, cost %s seconds, QPS:%s' % (requestNum, cost, requestNum / cost  ) )

        tServer = threading.Thread(target=create_server)
        tServer.start()
        time.sleep(5)
        tClient = threading.Thread(target=create_client)
        tClient.start()

if __name__ == '__main__':
    #测试其他
    unittest.main()