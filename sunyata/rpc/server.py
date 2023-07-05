from sunyata.rpc.protocal import TcpProtocal, UdpProtocal, HttpProtocal, RpcProtocal
import multiprocessing
from sunyata.rpc.exception import FuncNotFoundException
import queue
import threading
import socket
from sunyata.rpc.discovery import DiscoveryConfig, RpcDiscovery
import struct
from sunyata.rpc.compress import RpcCompress
from types import FunctionType
from sunyata.rpc.method import RpcMethod
import asyncio
import uvloop
import inspect
from sunyata.http.server import HttpServer
from sunyata.table_writer import TableWriter
import time
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class RpcServer(object):

    funcMap = {}
    funcList = []

    def __init__(self):
        self.discoveryConfig = None
        self.discovery = None
        self.protocal = RpcProtocal()
        self.accessLog = True

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

    @classmethod
    def getRegistedMethods(cls):
        return list(cls.funcMap.keys())

    def run(self, func, args, kwargs):
        try:
            if func not in self.funcList:
                return FuncNotFoundException('func not found')
            methodObj = self.funcMap[func]
            args = tuple(args)
            begin = time.time() * 1000
            if len(args) == 0 and len(kwargs) == 0:
                resp = methodObj.call()
            else:
                resp = methodObj.call(*args, **kwargs)
            end = time.time() * 1000
            cost = end - begin
            if self.accessLog:
                print("time:%s, method:%s, args:%s, cost:%sms" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), func, str(args), round(cost, 6)))
            return resp
        except Exception as ex:
            return Exception('server exception, ' + str(ex))

    def setDiscoverConfig(self, config: DiscoveryConfig):
        self.discoveryConfig = config
        self.discovery = RpcDiscovery(self.discoveryConfig.consulHost, self.discoveryConfig.consulPort, self.discoveryConfig.consulToken, self.discoveryConfig.etcdHost, self.discoveryConfig.etcdPort)

    def setKeepaliveTimeout(self, keepaliveTimeout: int):
        self.protocal.transport.setKeepaliveTimeout(keepaliveTimeout)

    @classmethod
    def rpc(cls, func):
        cls.regist(func)
        return func
    
    def printLogo(self):
        logo = """"""
        print(logo)

    def dumpRpcFuncs(self):
        twHeaders = ['RPC Methods']
        twRows = [ [elem] for elem in self.funcList ]
        tw = TableWriter(twHeaders, list(twRows))
        tw.dump()


class SimpleTcpRpcServer(RpcServer):
    
    def __init__(self, host, port):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.protocal = TcpProtocal(host, port)
    
    def serve(self):
        self.protocal.transport.bind(self.keepaliveTimeout)
        self.printLogo()
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
        self.dumpRpcFuncs()
        if self.discovery and self.discoveryConfig:
            self.discovery.regist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
        while 1:
            conn, _ = self.protocal.transport.accept()
            t = threading.Thread(target=self.handle, args=(conn,) )
            t.setDaemon(True)
            t.start()


class HttpRpcServer(RpcServer):
    
    def __init__(self, host, port, workers = multiprocessing.cpu_count()):
        RpcServer.__init__(self)
        self.host = host
        self.port = port
        self.protocal = HttpProtocal(host, port, workers)
        self.app = HttpServer(self.host, self.port)
        self.app.addRoute('/', self.handle)

    def handle(self, request):
        body = request.body
        resp = self.callback(body)
        return resp
        
    def callback(self, package):
        isEnableCompress = package[:1]
        msg = package[1:]
        if isEnableCompress == b'1':
            msg = RpcCompress.decompress(msg)
        request = self.protocal.unserialize(msg)
        func, args, kwargs = self.protocal.parseRequest(request)
        resp = self.run(func, args, kwargs)
        resp = self.protocal.serialize(resp)
        return resp
    
    async def asyncServe(self):
        tasks = []
        tasks.append(asyncio.create_task(self.app.asyncServe()))
        if self.discovery and self.discoveryConfig:
            registTask = asyncio.create_task(self.discovery.asyncRegist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True))
            tasks.append(registTask)
        await asyncio.wait(tasks)

    def serve(self):
        print('http rpc running on http://%s:%s' % (self.host, self.port) )
        self.dumpRpcFuncs()
        asyncio.run(self.asyncServe())


class TcpRpcServer(BlockTcpRpcServer):

    def __init__(self, host, port):
        BlockTcpRpcServer.__init__(self, host, port)
        self.host = host
        self.port = port
    
    async def handle(self, reader, writer):
        while 1:
            try:
                data = await reader.read(5)
                if data == b'':
                    raise Exception('peer closed')
                lengthField = data[:4]
                compressField = data[4:5]
                isEnableCompress = 0
                if compressField == b'1':
                    isEnableCompress = 1
                toread = struct.unpack("i", lengthField)[0]
                msg = b''
                readn = toread 
                while 1:
                    rmsg = await reader.read(readn)
                    if rmsg == b'':
                        raise Exception('peer closed')
                    msg = msg + rmsg
                    if len(msg) == toread:
                        readn = toread - len(rmsg)
                        break
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
                #print(ex, traceback.format_exc())
                writer.close()
                return

    async def main(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle, self.host, self.port, loop=loop)
        server = loop.run_until_complete(coro)
        print('tcp rpc running on tcp://%s:%s' % (self.host, self.port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

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
        loop = asyncio.get_event_loop()
        tasks = []
        tRegist = None
        if self.discovery and self.discoveryConfig:
            tRegist = self.discovery.asyncRegist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)
            tasks.append(tRegist)
        coro = asyncio.start_server(self.handle, self.host, self.port, loop=loop)
        tasks.append(coro)
        print('tcp rpc running on tcp://%s:%s' % (self.host, self.port) )
        self.dumpRpcFuncs()
        rs = loop.run_until_complete(asyncio.gather(*tasks))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server = rs[-1]
        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


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
            t.setDaemon(True)
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
                print('UDP handler exception:', ex)

    async def handlePackage(self):
        while 1:
            try:
                msg, cliAddr = self.protocal.transport.recv()
                self.queue.put({'msg' : msg, 'addr' : cliAddr})
            except socket.timeout:
                pass

    async def asyncServe(self):
        self.startWorkers()
        self.protocal.transport.bind()
        self.printLogo()
        print('udp rpc running on udp://%s:%s' % (self.host, self.port))
        self.dumpRpcFuncs()
        tasks = []
        if self.discovery and self.discoveryConfig:
            tasks.append(asyncio.create_task(self.discovery.asyncRegist(self.discoveryConfig.serviceName, self.discoveryConfig.serviceHost, self.discoveryConfig.servicePort, ttlHeartBeat=True)))
        tasks.append(asyncio.create_task(self.handlePackage()))
        loop = asyncio.get_event_loop()
        rs = loop.run_until_complete(asyncio.gather(*tasks))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server = rs[-1]
        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
    
    def serve(self):
        asyncio.run(self.asyncServe())


rpc = RpcServer.rpc