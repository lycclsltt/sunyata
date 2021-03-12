#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal, UdpProtocal
from agileutil.rpc.exception import FuncNotFoundException


class RpcClient(object): pass


class TcpRpcClient(RpcClient):

    def __init__(self, host, port, keepconnect = True):
        self.host = host
        self.port = port
        self.keepconnect = keepconnect
        self.protocal = TcpProtocal(host, port)

    def call(self, func, args = ()):
        if args == None: args = ()
        try:
            self.protocal.transport.connect()
        except Exception as ex:
            pass

        package = {
            'func' : func,
            'args' : args,
        }
        msg = self.protocal.serialize(package)
        self.protocal.transport.send(msg)
        respmsg = self.protocal.transport.recv()
        resp = self.protocal.unserialize(respmsg)
        if isinstance(resp, Exception):
            if not self.keepconnect: self.protocal.transport.close()
            raise resp
        if not self.keepconnect: self.protocal.transport.close()
        return resp

    def close(self):
        self.protocal.transport.close()


class UdpRpcClient(RpcClient):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.protocal = UdpProtocal(host, port)

    def call(self, func, args):
        package = {
            'func' : func,
            'args' : args,
        }
        msg = self.protocal.serialize(package)
        self.protocal.transport.send(msg)
        respmsg, _ = self.protocal.transport.recv()
        resp = self.protocal.unserialize(respmsg)
        if isinstance(resp, FuncNotFoundException):
            raise resp
        return resp