from agileutil.http.request import HttpRequest
from agileutil.http.response import HttpResponse
from agileutil.util import bytes2str

class HttpFactory(object):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def genLineHeaderBody(self, lines):
        reqLine = ''
        reqHeaders = []
        reqBody = ''
        lenLines = len(lines)
        for index, line in enumerate(lines):
            if index == 0: 
                reqLine = line
            elif index == lenLines - 1:
                reqBody = line
            elif index > 0 and line != '':
                reqHeaders.append(line)
        return reqLine, reqHeaders, reqBody
        
    @classmethod
    def genHttpRequest(cls, linesStr):
        linesStr = bytes2str(linesStr)
        req = HttpRequest()
        lines = linesStr.split("\r\n")
        reqLine, reqHeaders, reqBody = cls.genLineHeaderBody(lines)
        req.method, uri, req.httpVersion = reqLine.split(' ')
        req.uri = uri.split('?')[0]
        req.body = reqBody
        for header in reqHeaders:
            k, v = header.split(': ')
            req.headers[k] = v
        if req.body:
            for kvPair in req.body.split('&'):
                k, v = kvPair.split('=')
                req.data[k] = v
        else:
            kvPairs = uri.split('?')[1].split('&')
            for kvPair in kvPairs:
                k, v = kvPair.split('=')
                req.data[k] = v
        return req

    @classmethod
    def genHttpResponse(cls, status, body = ''):
        httpResponse = HttpResponse()
        httpResponse.status = status
        httpResponse.body = body
        return httpResponse