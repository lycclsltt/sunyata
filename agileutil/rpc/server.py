from agileutil.rpc.protocal import TcpProtocal, UdpProtocal, HttpProtocal, RpcProtocal
import multiprocessing
from agileutil.rpc.exception import FuncNotFoundException
import queue
import threading
import select
import socket
from agileutil.rpc.discovery import DiscoveryConfig, ConsulRpcDiscovery
import struct
import functools
from agileutil.sanic import SanicController
from agileutil.rpc.compress import RpcCompress
from types import MethodType,FunctionType,CoroutineType
from agileutil.rpc.method import RpcMethod
import asyncio
import inspect
from agileutil.eventloop import EventLoop

class RpcServer(object):

    funcMap = {}
    funcList = []
    isPrintLogo = True

    def __init__(self):
        #self.funcMap = {}
        #self.funcList = []
        self.discoveryConfig = None
        self.discovery = None
        self.protocal = RpcProtocal()

    @classmethod
    def regist(cls, func):
        if isinstance(func, FunctionType):
            if inspect.iscoroutinefunction(func):
                cls.funcMap[ func.__name__ ] = RpcMethod(RpcMethod.TYPE_WITHOUT_CLASS, func, isCoroutine=True)
                cls.funcList = cls.funcMap.keys()
            else:
                cls.funcMap[ func.__name__ ] = RpcMethod(RpcMethod.TYPE_WITHOUT_CLASS, func)
                cls.funcList = cls.funcMap.keys()
        else:
            classDefine = func
            serMethods = list( filter(lambda m: not m.startswith('_'), dir(classDefine)) )
            for methodName in serMethods:
                funcName = "{}.{}".format(classDefine.__name__, methodName)
                funcObj = getattr(classDefine, methodName)
                if inspect.iscoroutinefunction(funcObj):
                    cls.funcMap [ funcName ] = RpcMethod(RpcMethod.TYPE_WITH_CLASS, funcObj, classDefine, isCoroutine=True)
                    cls.funcList = cls.funcMap.keys()
                else:
                    cls.funcMap [ funcName ] = RpcMethod(RpcMethod.TYPE_WITH_CLASS, funcObj, classDefine)
                    cls.funcList = cls.funcMap.keys()

    def run(self, func, args, kwargs):
        try:
            if func not in self.funcList:
                return FuncNotFoundException('func not found')
            methodObj = self.funcMap[func]
            args = tuple(args)
            if len(args) == 0 and len(kwargs) == 0:
                resp = methodObj.call()
            else:
                resp = methodObj.call(*args, **kwargs)
            return resp
        except Exception as ex:
            return Exception('server exception, ' + str(ex))

    def setDiscoverConfig(self, config: DiscoveryConfig):
        self.discoveryConfig = config
        self.discovery = ConsulRpcDiscovery(self.discoveryConfig.consulHost, self.discoveryConfig.consulPort)

    def setKeepaliveTimeout(self, keepaliveTimeout: int):
        self.protocal.transport.setKeepaliveTimeout(keepaliveTimeout)

    @classmethod
    def rpc(cls, func):
        cls.regist(func)

    def printLogo(self):
        if self.isPrintLogo == False:
            return
        logo = """
     _         _ _      _   _ _   _ _ 
    / \   __ _(_) | ___| | | | |_(_) |
   / _ \ / _` | | |/ _ \ | | | __| | |
  / ___ \ (_| | | |  __/ |_| | |_| | |
 /_/   \_\__, |_|_|\___|\___/ \__|_|_|
         |___/      
 
 RPC server is ready! 
         """
        print(logo)


class SimpleTcpRpcServer(RpcServer):
    
    def __init__(self, host, port):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.protocal = TcpProtocal(host, port)
    
    def serve(self):
        self.protocal.transport.bind(self.keepaliveTimeout)
        while 1:
            msg = self.protocal.transport.recv()
            request = self.protocal.unserialize(msg)
            func, args, kwargs = self.protocal.parseRequest(request)
            resp = self.run(func, args, kwargs)
            self.protocal.transport.send(self.protocal.serialize(resp))


class BlockTcpRpcServer(SimpleTcpRpcServer):
    
    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        SimpleTcpRpcServer.__init__(self, host, port)
        self.worker = workers

    def handle(self, conn):
        while 1:
            try:
                msg = self.protocal.transport.recvPeer(conn)
                request = self.protocal.unserialize(msg)
                func, args, kwargs = self.protocal.parseRequest(request)
                resp = self.run(func, args, kwargs)                    
                self.protocal.transport.sendPeer(self.protocal.serialize(resp), conn)
            except Exception as ex:
                conn.close()
                return

    def serve(self):
        self.protocal.transport.bind()
        self.printLogo()
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        while 1:
            conn, _ = self.protocal.transport.accept()
            t = threading.Thread(target=self.handle, args=(conn,) )
            t.start()


class HttpRpcServerController(SanicController):
    
    callBack = None

    async def handle(self):
        self.isRaw = True
        body = self.body()
        return self.callBack(body)

    @classmethod
    def setCallback(cls, callBack):
        cls.callBack = callBack


class HttpRpcServer(RpcServer, SanicController):
    
    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.worker = workers
        self.protocal = HttpProtocal(host, port, workers)
        HttpRpcServerController.setCallback(self.handle)
        self.protocal.transport.app.route('/', HttpRpcServerController)
        
    def handle(self, package):
        isEnableCompress = package[:1]
        msg = package[1:]
        if isEnableCompress == b'1':
            msg = RpcCompress.decompress(msg)
        request = self.protocal.unserialize(msg)
        func, args, kwargs = self.protocal.parseRequest(request)
        resp = self.run(func, args, kwargs)
        resp = self.protocal.serialize(resp)
        return resp

    def serve(self):
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        self.printLogo()
        self.protocal.transport.app.run()

    def disableLog(self):
        self.protocal.transport.app.disableLog()


class TcpRpcServer(BlockTcpRpcServer):

    def __init__(self, host, port):
        BlockTcpRpcServer.__init__(self, host, port)
        self.host = host
        self.port = port
    
    async def handle(self, reader, writer):
        while 1:
            try:
                data = await reader.read(5)
                lengthField = data[:4]
                compressField = data[4:5]
                isEnableCompress = 0
                if compressField == b'1':
                    isEnableCompress = 1
                toread = struct.unpack("i", lengthField)[0]
                msg = await reader.read(toread)
                if isEnableCompress:
                    msg = RpcCompress.decompress(msg)

                request = self.protocal.unserialize(msg)
                func, args, kwargs = self.protocal.parseRequest(request)
                resp = await self.run(func, args, kwargs) 
                respbytes = self.protocal.serialize(resp)

                isEnableCompress = b'0'
                if len(msg) >= RpcCompress.enableCompressLen:
                    isEnableCompress = b'1'
                    respbytes = RpcCompress.compress(respbytes)
                lenbytes = struct.pack("i", len(respbytes))
                writer.write( lenbytes + isEnableCompress + respbytes)
            except Exception as ex:
                writer.close()
                return

    async def main(self):
        server = await asyncio.start_server(self.handle, self.host, self.port)
        addr = server.sockets[0].getsockname()
        self.printLogo()
        async with server:
            await server.serve_forever()

    async def run(self, func, args, kwargs):
        try:
            if func not in self.funcList:
                return FuncNotFoundException('func not found')
            methodObj = self.funcMap[func]
            args = tuple(args)
            if len(args) == 0 and len(kwargs) == 0:
                resp = await methodObj.asyncCall()
            else:
                resp = await methodObj.asyncCall(*args, **kwargs)
            return resp
        except Exception as ex:
            return Exception('server exception, ' + str(ex))

    def serve(self):
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        EventLoop.runUntilComplete( self.main() )


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
            try:
                body = self.queue.get()
                addr = body.get('addr')
                msg = body.get('msg')
                request = self.protocal.unserialize(msg)
                func, args, kwargs = self.protocal.parseRequest(request)
                resp = self.run(func, args, kwargs)
                self.protocal.transport.sendPeer(self.protocal.serialize(resp), addr = addr)
            except Exception as ex:
                print('udp handler exception:', ex)
    
    def serve(self):
        self.startWorkers()
        self.protocal.transport.bind()
        self.printLogo()
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        while 1:
            try:
                msg, cliAddr = self.protocal.transport.recv()
                self.queue.put({'msg' : msg, 'addr' : cliAddr})
            except socket.timeout:
                pass


rpc = RpcServer.rpc