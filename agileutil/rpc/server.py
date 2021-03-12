#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal, UdpProtocal
import multiprocessing
from agileutil.rpc.exception import FuncNotFoundException
import queue
import threading
import select
import socket


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


class AsyncTcpRpcServer(TcpRpcServer):

    def __init__(self, host, port):
        TcpRpcServer.__init__(self, host, port)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = (self.host, self.port)
        self.timeout = 10
        self.epoll = select.epoll()
        self.fdToSocket = {self.socket.fileno():self.socket}
        self.fdResp = {}

    def bind(self):
        self.socket.bind(self.addr)
        self.socket.listen(10)
        self.socket.setblocking(False)
        self.epoll.register(self.socket.fileno(), select.EPOLLIN)

    def serve(self):
        self.bind()
        while 1:
            events = self.epoll.poll(self.timeout)
            if not events:
                print("epoll超时无活动连接，重新轮询......")
                continue
            print("有" , len(events), "个新事件，开始处理......")
            for fd, event in events:
                socket = self.fdToSocket[fd]
                if socket == self.socket:
                    conn, addr = self.socket.accept()
                    print("新连接：" , addr)
                    conn.setblocking(False)
                    self.epoll.register(conn.fileno(), select.EPOLLIN)
                    self.fdToSocket[conn.fileno()] = conn
                elif event & select.EPOLLHUP:
                    print('client close')
                    self.epoll.unregister(fd)
                    self.fdToSocket[fd].close()
                    del self.fdToSocket[fd]
                elif event & select.EPOLLIN:
                    msg = self.protocal.transport.recv(socket)
                    request = self.protocal.unserialize(msg)
                    func, args = self.protocal.parseRequest(request)
                    resp = self.run(func, args)
                    self.fdResp[fd] = resp
                    self.epoll.modify(fd, select.EPOLLOUT)
                elif event & select.EPOLLOUT:
                    if fd in self.fdResp:
                        resp = self.fdResp[fd]
                        self.protocal.transport.send(self.protocal.serialize(resp), socket)
                        self.epoll.modify(fd, select.EPOLLIN)
                        socket.close()


class UdpRpcServer(RpcServer):

    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        RpcServer.__init__(self)
        self.protocal = UdpProtocal(host, port)
        self.worker = workers
        self.queueMaxSize = 100000
        self.queue = queue.Queue(self.queueMaxSize)

    def startWorkers(self):
        for i in range(self.worker):
            t = threading.Thread(target=self.handle)
            t.start()

    def handle(self):
        while 1:
            body = self.queue.get()
            addr = body.get('addr')
            msg = body.get('msg')
            request = self.protocal.unserialize(msg)
            func, args = self.protocal.parseRequest(request)
            resp = self.run(func, args)
            self.protocal.transport.send(self.protocal.serialize(resp), addr = addr)
    
    def serve(self):
        self.startWorkers()
        self.protocal.transport.bind()
        while 1:
            msg, cliAddr = self.protocal.transport.recv()
            self.queue.put({'msg' : msg, 'addr' : cliAddr})

            