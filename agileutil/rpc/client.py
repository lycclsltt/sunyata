#coding=utf-8

from agileutil.rpc.protocal import TcpProtocal
from agileutil.rpc.exception import FuncNotFoundException


class RpcClient(object): pass


class TcpRpcClient(RpcClient):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connstr = "tcp://%s:%s" % (host, port)
        self.protocal = TcpProtocal(host, port)

    def call(self, func, args):
        self.protocal.transport.connect()
        package = {
            'func' : func,
            'args' : args,
        }
        msg = self.protocal.serialize(package)
        self.protocal.transport.send(msg)
        respmsg = self.protocal.transport.recv()
        resp = self.protocal.unserialize(respmsg)
        if isinstance(resp, FuncNotFoundException):
            self.protocal.transport.close()
            raise resp
        self.protocal.transport.close()
        return resp