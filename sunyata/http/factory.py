from datetime import date
from sunyata.http.request import HttpRequest
from sunyata.http.response import HttpResponse
from sunyata.http.router import HttpRouter
from sunyata.util import bytes2str

class HttpFactory(object):

    maxContentLength = 1 * 1024 * 1024 #1M限制

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
        '''
        reqHeaders = []
        reqLine = lines[0]
        for l in lines[1:]:
            if l and b': ' in l:
                reqHeaders.append(l)
            else:
                reqHeaders = [l for l in lines[1:-2] if l != b'' and b': ' in l]
        '''
            
        #reqBody = lines[-1]
        #reqHeaders = [l for l in lines[1:-2] if l != b'' and b': ' in l]
        return reqLine, reqHeaders, reqBody
        '''
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
        '''
        
    @classmethod
    def genHttpRequest(cls, linesStr, conn):
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
        contentLength = int(req.headers.get('Content-Length'))
        #if contentLength > cls.maxContentLength:
        #    raise Exception('content-length over')
        hasRead = len(req.body)
        toRead = contentLength - hasRead
        bufsize = 1024 
        while toRead:
            rdata = conn.recv(bufsize)
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