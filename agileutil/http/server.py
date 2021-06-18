from agileutil.http.factory import HttpFactory
from agileutil.http.status import *
from traceback import format_exc
from agileutil.eventloop import EventLoop
import asyncio

class HttpServer(object):

    routerMap = {}

    def __init__(self, bind = '0.0.0.0', port=9989 ):
        super().__init__()
        self.bind = bind
        self.port = port
        self.bufSize = 10240
    
    @classmethod
    def addRoute(cls, path, func, methods = None):
        cls.routerMap[path] = HttpFactory.genHttpRouter(path, func, methods)

    def printLogo(self):
        logo = """
     _         _ _      _   _ _   _ _ 
    / \   __ _(_) | ___| | | | |_(_) |
   / _ \ / _` | | |/ _ \ | | | __| | |
  / ___ \ (_| | | |  __/ |_| | |_| | |
 /_/   \_\__, |_|_|\___|\___/ \__|_|_|
         |___/      
 
 HTTP server listening on %s:%s 
         """  % (self.bind, self.port)
        print(logo)

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

    def serve(self):
        self.listenAndServe()

    @classmethod
    def route(cls, path, methods = None):
        def wrapper(func):
            cls.addRoute(path, func, methods)
            return func
        return wrapper

route = HttpServer.route