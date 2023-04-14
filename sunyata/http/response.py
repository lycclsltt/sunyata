from sunyata.util import str2bytes, bytes2str
import ujson

class HttpResponse(object):

    __slots__ = ('httpVersion', 'status', 'headers', 'body')

    def __init__(self, status, body) -> None:
        super().__init__()
        self.httpVersion = 'HTTP/1.1'
        self.status = status
        self.headers = {}
        self.body = body

    def genHeaders(self):
        self.headers['Content-Type'] = 'text/html'
        self.headers['Content-Length'] = len(self.body)

    def toBytes(self):
        resLine = f"{self.httpVersion} {self.status.code} {self.status.msg}"
        self.genHeaders()
        resHeaders = ''
        for k, v in self.headers.items():
            resHeaders += f"{k}: {v}\r\n"
        resHeaders += "\r\n"
        resBody = self.body
        if type(resBody) == str:
            resBody = str2bytes(resBody)
        res = str2bytes(resLine + resHeaders) + resBody
        return res
    
    def responseBody(self):
        resBody = self.body
        if type(resBody) == str:
            resBody = str2bytes(resBody)
        return resBody
    
    @classmethod
    def responseConvertSetToJson(cls, resp):
        return ujson.encode(list(resp))
    
    @classmethod
    def responseConverBytesToStr(cls, resp):
        return bytes2str(resp)
    
    @classmethod
    def responseConvertToJson(cls, resp):
        return ujson.encode(resp)
    
    @classmethod
    def responseConvertToBytes(cls, resp):
        return bytes(resp)
    
    @classmethod
    def responseConvertToStr(cls, resp):
        return str(resp)
    
    @classmethod
    def responseConvertRaw(self, resp):
        return resp