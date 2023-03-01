from sunyata.http.factory import HttpFactory
from sunyata.http.status import *
from traceback import format_exc
from sunyata.http.transport import TcpTransport
from multiprocessing import cpu_count
from types import MethodType,FunctionType
import asyncio
import queue
import threading

class HttpServer(object):

    __slots__ = ('bind', 'port', 'bufSize', 'transport', 'queueSize', 'queue', 'threadList', 'workers', 'isAsync', 'exitFlag', 'maxContentLength')

    routerMap = {}

    def __init__(self, bind = '0.0.0.0', port=9989, isAsync=False, workers = cpu_count()):
        super().__init__()
        self.bind = bind
        self.port = port
        self.bufSize = 10240
        self.transport = TcpTransport(self.bind, self.port)
        self.queueSize = 30000
        self.queue = queue.Queue(self.queueSize)
        self.threadList = []
        self.workers = workers
        self.isAsync = isAsync
        self.exitFlag = False
        self.maxContentLength = 1 * 1024 * 1024 # 1M限制
    
    @classmethod
    def addRoute(cls, path, func, methods = None):
        if isinstance(func, FunctionType) or isinstance(func, MethodType):
            cls.routerMap[path] = HttpFactory.genHttpRouter(path, func, methods)
        elif isinstance(func, object):
            controllerObj = func()
            if not path.endswith('/'): path += '/'
            for classFunc in dir(controllerObj):
                if classFunc.startswith('_'):
                    continue
                cls.routerMap[path + classFunc] = HttpFactory.genHttpRouter(path + classFunc, getattr(controllerObj, classFunc), methods)


    async def handleRequest(self, httpRequest):
        router = self.routerMap.get(httpRequest.uri, None)
        if not router:
            return HttpFactory.genHttpResponse(HttpStatus404)
        if router.methods and httpRequest.method not in router.methods:
            return HttpFactory.genHttpResponse(HttpStatus405)
        try:
            respString = await router.getFunc()(httpRequest)
            return HttpFactory.genHttpResponse(HttpStatus200, respString)
        except Exception as ex:
            return HttpFactory.genHttpResponse(HttpStatus500, format_exc())

    def syncHandleRequest(self, httpRequest):
        router = self.routerMap.get(httpRequest.uri, None)
        if not router:
            return HttpFactory.genHttpResponse(HttpStatus404)
        if router.methods and httpRequest.method not in router.methods:
            return HttpFactory.genHttpResponse(HttpStatus405)
        try:
            respString = router.getFunc()(httpRequest)
            return HttpFactory.genHttpResponse(HttpStatus200, respString)
        except Exception as ex:
            return HttpFactory.genHttpResponse(HttpStatus500, format_exc())
    
    async def handleEcho(self, reader, writer):
        data = await reader.read(self.bufSize)
        if data == b'': return
        #addr = writer.get_extra_info('peername')
        httpRequest = HttpFactory.genHttpRequest(data)
        httpResponse = await self.handleRequest(httpRequest)
        writer.write(httpResponse.toBytes())
        await writer.drain()
        writer.close()
    
    def listenAndServe(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handleEcho, self.bind, self.port, loop=loop)
        server = loop.run_until_complete(coro)
        print('Http Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        loop.run_until_complete(server.wait_closed())
        print('Http Server Closed.')
        loop.close()

    def handleConn(self, conn):
        data = conn.recv(self.maxContentLength)
        if not data:
            conn.close()
            return
        req = HttpFactory.genHttpRequest(data, conn)
        resp = self.syncHandleRequest(req)
        self.transport.sendAll(conn, resp.toBytes())
        conn.close()

    def workServe(self):
        while self.exitFlag == False:
            try:
                conn = self.queue.get(block=True, timeout=1)
                self.handleConn(conn)
            except queue.Empty:
                pass
            except Exception as ex:
                print(ex, format_exc())

    def listenAndDispatch(self):
        for i in range(self.workers):
            th = threading.Thread(target=self.workServe)
            th.start()
            self.threadList.append(th)
            print('Start worker %s' % th )
        self.transport.bind()
        while True:
            try:
                conn, _ = self.transport.accept()
                self.queue.put(conn, block=False)
            except KeyboardInterrupt:
                print('Server is closing...')
                self.exitFlag = True
                for th in self.threadList:
                    th.join()
                self.transport.close()
                print('Server closed.')
                return
            except Exception as ex:
                print(ex, format_exc())

    def serve(self):
        if self.isAsync:
            self.listenAndServe()
        else:
            self.listenAndDispatch()

    @classmethod
    def route(cls, path, methods = None):
        def wrapper(func):
            cls.addRoute(path, func, methods)
            return func
        return wrapper

route = HttpServer.route