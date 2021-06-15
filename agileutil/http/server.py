from agileutil.http.factory import HttpFactory
from agileutil.http.status import *
from traceback import format_exc
import asyncio


class HttpServer(object):

    routeMethodMap = {}

    def __init__(self, bind = '0.0.0.0', port=9989 ):
        super().__init__()
        self.bind = bind
        self.port = port
        self.bufSize = 10240
        
    def addRoute(self, route, method):
        self.routeMethodMap[route] = method

    async def handleRequest(self, httpRequest):
        method = self.routeMethodMap.get(httpRequest.uri, None)
        if not method:
            return HttpFactory.genHttpResponse(HttpStatus404)
        try:
            respString = await method(httpRequest)
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
    
    async def listenAndServe(self):
        server = await asyncio.start_server(self.handleEcho, self.bind, self.port)
        print('Http server listening on %s:%s' % (self.bind, self.port) )
        async with server: await server.serve_forever()

    def serve(self):
        return asyncio.run(self.listenAndServe())

    @classmethod
    def route(cls, path):
        def wrapper(method):
            cls.routeMethodMap[path] = method
            return method
        return wrapper

route = HttpServer.route