from agileutil.http.request import HttpRequest
from agileutil.http.response import HttpResponse
from agileutil.http.router import HttpRouter
from agileutil.util import bytes2str

class HttpFactory(object):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def genLineHeaderBody(self, lines):
        reqLine = b''
        reqHeaders = []
        reqBody = b''
        lenLines = len(lines)
        for index, line in enumerate(lines):
            if index == 0: 
                reqLine = line
            elif index == lenLines - 1:
                reqBody = line
            elif index > 0 and line != b'':
                reqHeaders.append(line)
        return reqLine, reqHeaders, reqBody
        
    @classmethod
    def genHttpRequest(cls, linesStr):
        req = HttpRequest()
        lines = linesStr.split(b"\r\n")
        reqLine, reqHeaders, reqBody = cls.genLineHeaderBody(lines)
        method, uri, httpVersion = reqLine.split(b' ')
        req.method = bytes2str(method)
        req.httpVersion = bytes2str(httpVersion)
        req.uri = bytes2str( uri.split(b'?')[0] )
        req.body = reqBody
        for header in reqHeaders:
            k, v = header.split(b': ')
            req.headers[bytes2str(k)] = bytes2str(v)
        if req.body:
            try:
                for kvPair in req.body.split(b'&'):
                    k, v = kvPair.split(b'=')
                    req.data[bytes2str(k)] = bytes2str(v)
            except:
                pass
        else:
            try:
                kvPairs = uri.split(b'?')[1].split(b'&')
                for kvPair in kvPairs:
                    k, v = kvPair.split(b'=')
                    req.data[bytes2str(k)] = bytes2str(v)
            except:
                pass
        return req

    @classmethod
    def genHttpResponse(cls, status, body = ''):
        httpResponse = HttpResponse()
        httpResponse.status = status
        httpResponse.body = body
        return httpResponse

    @classmethod
    def genHttpRouter(cls, path, func, methods):
        httpRouter = HttpRouter()
        httpRouter.path = path
        httpRouter.func = func
        httpRouter.methods = methods
        return httpRouter