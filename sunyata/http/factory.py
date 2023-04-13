from sunyata.http.request import HttpRequest
from sunyata.http.response import HttpResponse
from sunyata.http.router import HttpRouter
from sunyata.util import bytes2str
import ujson

class HttpFactory(object):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def genLineHeaderBody(self, lines):
        getHeader = 1
        reqHeaders = []
        reqBody = b''
        reqLine = lines[0]
        for l in lines[1:]:
            if not l:
                getHeader = 0
            if getHeader:
                reqHeaders.append(l)
            else:
                reqBody = reqBody + l
        return reqLine, reqHeaders, reqBody

    @classmethod
    def parseRequestData(cls, uri, body):
        requestData = {}
        if uri:
            try:
                kvPairs = uri.split(b'?')[1].split(b'&')
                for kvPair in kvPairs:
                    k, v = kvPair.split(b'=')
                    requestData[bytes2str(k)] = bytes2str(v)
            except:
                pass
        if body:
            try:
                bodydic = ujson.decode(body)
                requestData.update(bodydic)
            except:
                pass
        return requestData
        
    @classmethod
    async def genHttpRequest(cls, requestStream):
        linesStr = await requestStream.reader.read(requestStream.bufsize)
        req = HttpRequest()
        lines = linesStr.split(b"\r\n")
        reqLine, reqHeaders, reqBody = cls.genLineHeaderBody(lines)
        method, uri, httpVersion = reqLine.split(b' ')
        req.method = bytes2str(method)
        req.httpVersion = bytes2str(httpVersion)
        req.uri = bytes2str( uri.split(b'?')[0] )
        req.body = reqBody
        for header in reqHeaders:
            if header == b'':
                continue
            k, v = header.split(b': ')
            try:
                req.headers[bytes2str(k)] = bytes2str(v)
            except:
                req.headers[str(k)] = str(v)
        req.data = cls.parseRequestData(uri, req.body)
        contentLength = int(req.headers.get('Content-Length', 0))
        hasRead = len(req.body)
        toRead = contentLength - hasRead
        while toRead:
            rdata = requestStream.reader.read(toRead)
            if not rdata:
                raise Exception('peer closed')
            req.body = req.body + rdata
            hasRead = hasRead + len(rdata)
            toRead = contentLength - hasRead
        return req

    @classmethod
    def genHttpResponse(cls, status, body = ''):
        return HttpResponse(status, body)

    @classmethod
    def genHttpRouter(cls, path, func, methods):
        httpRouter = HttpRouter()
        httpRouter.path = path
        httpRouter.func = func
        httpRouter.methods = methods
        return httpRouter