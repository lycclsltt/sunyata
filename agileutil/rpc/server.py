#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal
import multiprocessing
from agileutil.rpc.exception import FuncNotFoundException


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


class TcpRpcServer(RpcServer):

    def __init__(self, host, port):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.protocal = TcpProtocal(host, port)
        self.worker = multiprocessing.cpu_count()
    
    def serve(self):
        self.protocal.transport.bind()
        while 1:
            msg = self.protocal.transport.recv()
            request = self.protocal.unserialize(msg)
            func, args = self.protocal.parseRequest(request)
            resp = self.run(func, args)
            self.protocal.transport.send(self.protocal.serialize(resp))