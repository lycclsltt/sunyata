from sunyata.http.factory import HttpFactory
from sunyata.http.status import *
import uvicorn
from sunyata.http.rawserver import RawHttpServer
from sunyata.http.request import HttpRequest
import sunyata.util as util
import traceback


class HttpServer(RawHttpServer):

    routerMap = {}

    def __init__(self, bind = '0.0.0.0', port=9989, log_level='error'):
        RawHttpServer.__init__(self, bind=bind, port=port)
        self.config = uvicorn.Config("sunyata.http.server:HttpServer", host=self.bind, port=self.port, log_level=log_level)

    def serve(self):
        server = uvicorn.Server(self.config)
        print('http running on http://%s:%s' % (self.bind, self.port) )
        server.run()
    
    async def genHttpRequest(self, scheme, httpVersion, method, path, queryString, headers, body, clientTuple):
        httpRequest = HttpRequest()
        httpRequest.scheme = scheme
        httpRequest.httpVersion = httpVersion
        httpRequest.method = method
        httpRequest.uri = path
        httpRequest.queryString = queryString
        httpRequest.headers = headers
        httpRequest.body = body
        httpRequest.client.remoteAddr = clientTuple[0]
        httpRequest.client.port = clientTuple[1]
        httpRequest.data = HttpFactory.parseRequestData(util.str2bytes(path + "?") + queryString, body)
        return httpRequest

    async def readBody(self, receive):
        """
        Read and return the entire body from an incoming ASGI message.
        """
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        return body
    
    async def rawHeadersToDict(self, rawHeaders):
        headers = {}
        for line in rawHeaders:
            headers[util.bytes2str(line[0])] = str(util.bytes2str(line[1]))
        return headers

    async def __call__(self, scope, receive, send):
        assert scope['type'] == 'http'
        headers = await self.rawHeadersToDict(scope['headers'])
        body = await self.readBody(receive)
        try:
            httpRequest = await self.genHttpRequest(
                scope['scheme'],
                scope['http_version'],
                scope['method'], 
                scope['path'],  
                scope['query_string'],
                headers, 
                body,
                scope['client']
            )
            httpResponse = await self.handleRequest(httpRequest)
        except Exception as ex:
            print(str(ex) + ' ' + traceback.format_exc())
            httpResponse = HttpFactory.genHttpResponse(HttpStatus500, str(ex))
        await send(
            {
                "type": "http.response.start",
                "status": httpResponse.status.code,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send(
            {
                "type": "http.response.body", 
                "body": httpResponse.responseBody(),
            }
        )


route = HttpServer.route