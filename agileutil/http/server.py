from agileutil.rpc.transport import TcpTransport
from agileutil.http.factory import HttpFactory
from agileutil.http.status import *
from traceback import format_exc
import asyncio

class HttpServer(object):
    
    def __init__(self, bind = '0.0.0.0', port=9989 ) -> None:
        super().__init__()
        self.bind = bind
        self.port = port
        self.transport = TcpTransport(bind, port, timeout=30)
        self.routeMethodMap = {}

    def addRoute(self, route, method):
        self.routeMethodMap[route] = method

    def handleRequest(self, httpRequest):
        method = self.routeMethodMap.get(httpRequest.uri, None)
        if not method:
            return HttpFactory.genHttpResponse(HttpStatus404)
        try:
            respString = method(httpRequest)
            return HttpFactory.genHttpResponse(HttpStatus200, respString)
        except Exception as ex:
            return HttpFactory.genHttpResponse(HttpStatus500, format_exc())

    def serve(self):
        self.transport.bind()
        print('Http server listening on %s:%s' % (self.bind, self.port) )
        while True:
            conn, addr = self.transport.accept()
            data = conn.recv(10240)
            httpRequest = HttpFactory.genHttpRequest(data)
            httpResponse = self.handleRequest(httpRequest)
            conn.send(httpResponse.toBytes())
            conn.close()


class HttpServerV2(object):

    def __init__(self, bind = '0.0.0.0', port=9989 ):
        super().__init__()
        self.bind = bind
        self.port = port
        self.routeMethodMap = {}
        self.bufSize = 10240
        
    def addRoute(self, route, method):
        self.routeMethodMap[route] = method

    def handleRequest(self, httpRequest):
        method = self.routeMethodMap.get(httpRequest.uri, None)
        if not method:
            return HttpFactory.genHttpResponse(HttpStatus404)
        try:
            respString = method(httpRequest)
            return HttpFactory.genHttpResponse(HttpStatus200, respString)
        except Exception as ex:
            return HttpFactory.genHttpResponse(HttpStatus500, format_exc())
    
    async def handleEcho(self, reader, writer):
        data = await reader.read(self.bufSize)
        #addr = writer.get_extra_info('peername')
        httpRequest = HttpFactory.genHttpRequest(data)
        httpResponse = self.handleRequest(httpRequest)
        writer.write(httpResponse.toBytes())
        await writer.drain()
        writer.close()
    
    async def listenAndServe(self):
        server = await asyncio.start_server(self.handleEcho, self.bind, self.port)
        print('Http server listening on %s:%s' % (self.bind, self.port) )
        async with server: await server.serve_forever()

    def serve(self):
        return asyncio.run(self.listenAndServe())