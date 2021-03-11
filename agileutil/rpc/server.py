#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal
import multiprocessing
from agileutil.rpc.exception import FuncNotFoundException
import queue
import threading


class RpcServer(object):
    
    def __init__(self):
        self.funcMap = {}
        self.funcList = []

    def regist(self, func):
        self.funcMap[ func.__name__ ] = func
        self.funcList = self.funcMap.keys()

    def run(self, func, args):
        if func not in self.funcList:
            return FuncNotFoundException('func not found')
        funcobj = self.funcMap[func]
        resp = funcobj(args)
        return resp


class SimpleTcpRpcServer(RpcServer):
    
    def __init__(self, host, port):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.protocal = TcpProtocal(host, port)
    
    def serve(self):
        self.protocal.transport.bind()
        while 1:
            msg = self.protocal.transport.recv()
            request = self.protocal.unserialize(msg)
            func, args = self.protocal.parseRequest(request)
            resp = self.run(func, args)
            self.protocal.transport.send(self.protocal.serialize(resp))


class TcpRpcServer(SimpleTcpRpcServer):

    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        SimpleTcpRpcServer.__init__(self, host, port)
        self.worker = workers
        self.queueMaxSize = 100000
        self.queue = queue.Queue(self.queueMaxSize)

    def handle(self):
        while 1:
            conn = self.queue.get()
            msg = self.protocal.transport.recv(conn)
            request = self.protocal.unserialize(msg)
            func, args = self.protocal.parseRequest(request)
            resp = self.run(func, args)
            self.protocal.transport.send(self.protocal.serialize(resp), conn)
            conn.close()

    def startWorkers(self):
        for i in range(self.worker):
            t = threading.Thread(target=self.handle)
            t.start()

    def serve(self):
        self.startWorkers()
        self.protocal.transport.bind()
        while 1:
            conn, _ = self.protocal.transport.accept()
            self.queue.put(conn)