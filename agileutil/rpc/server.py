from agileutil.rpc.protocal import TcpProtocal, UdpProtocal, HttpProtocal, RpcProtocal
import multiprocessing
from agileutil.rpc.exception import FuncNotFoundException
import queue
import threading
import socket
from agileutil.rpc.discovery import DiscoveryConfig, ConsulRpcDiscovery
import struct
from agileutil.rpc.compress import RpcCompress
from types import FunctionType
from agileutil.rpc.method import RpcMethod
import asyncio
import inspect
from agileutil.http.server import HttpServer

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


class HttpRpcServer(RpcServer):
    
    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.protocal = HttpProtocal(host, port, workers)
        self.app = HttpServer(self.host, self.port)
        self.app.addRoute('/', self.handle)

    async def handle(self, request):
        body = request.body
        return await self.callback(body)
        
    async def callback(self, package):
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
        tRegist = None
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        self.printLogo()
        print(' HTTP serve on %s:%s' % (self.host, self.port) )
        self.app.serve()


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
        print(' TCP serve on %s:%s' % (self.host, self.port) )
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
        asyncio.run( self.asyncServe() )

    async def asyncServe(self):
        tRegist = None
        if self.discovery and self.discoveryConfig:
            tRegist = asyncio.create_task( self.discovery.asyncRegist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True) )
        tServer = asyncio.create_task( self.main() )
        await tServer
        if tRegist:
            await tRegist


class UdpRpcServer(RpcServer):

    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        RpcServer.__init__(self)
        self.protocal = UdpProtocal(host, port)
        self.worker = workers
        self.queueMaxSize = 100000
        self.queue = queue.Queue(self.queueMaxSize)
        self.host = host
        self.port = port

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
        print(' UDP serve on %s:%s' % (self.host, self.port))
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        while 1:
            try:
                msg, cliAddr = self.protocal.transport.recv()
                self.queue.put({'msg' : msg, 'addr' : cliAddr})
            except socket.timeout:
                pass


rpc = RpcServer.rpc