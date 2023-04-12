from sunyata.http.factory import HttpFactory
from sunyata.http.status import *
from sunyata.http.transport import TcpTransport
from sunyata.http.request_stream import RequestStream
from traceback import format_exc
from multiprocessing import cpu_count
from types import MethodType,FunctionType
import asyncio
import inspect

class HttpServer(object):

    __slots__ = ('bind', 'port', 'bufSize', 'transport', 'queueSize', 'queue', 'threadList', 'workers', 'isAsync', 'exitFlag', 'maxContentLength')

    routerMap = {}

    def __init__(self, bind = '0.0.0.0', port=9989, workers = cpu_count()):
        super().__init__()
        self.bind = bind
        self.port = port
        self.bufSize = 1024 * 1024
        self.transport = TcpTransport(self.bind, self.port)
        self.queueSize = 30000
        self.threadList = []
        self.workers = workers
        self.queue = asyncio.Queue(self.queueSize)
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
            if inspect.iscoroutinefunction(router.getFunc()):
                respString = await router.getFunc()(httpRequest)
            else:
                respString = router.getFunc()(httpRequest)
            return HttpFactory.genHttpResponse(HttpStatus200, respString)
        except Exception as ex:
            return HttpFactory.genHttpResponse(HttpStatus500, format_exc())
    
    async def acceptStream(self, reader, writer):
        try:
            requestStream = RequestStream(reader, writer)
            httpRequest = await HttpFactory.genHttpRequest(requestStream)
            httpResponse = await self.handleRequest(httpRequest)
        except Exception as ex:
            httpResponse = HttpFactory.genHttpResponse(HttpStatus500, str(ex))
        writer.write(httpResponse.toBytes())
        await writer.drain()
        writer.close()
    
    async def listenAndServe(self):
        tasklist = []
        server = await asyncio.start_server(self.acceptStream, self.bind, self.port)
        tasklist.append(server.serve_forever())
        for task in tasklist:
            await task

    def serve(self):
        asyncio.run(self.listenAndServe())

    @classmethod
    def route(cls, path, methods = None):
        def wrapper(func):
            cls.addRoute(path, func, methods)
            return func
        return wrapper

route = HttpServer.route