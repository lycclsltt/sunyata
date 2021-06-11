from agileutil.http.status import HttpStatus200
from agileutil.util import str2bytes

class HttpResponse(object):

    def __init__(self) -> None:
        super().__init__()
        self.httpVersion = 'HTTP/1.1'
        self.status = HttpStatus200()
        self.headers = {}
        self.body = ''

    def genHeaders(self):
        self.headers['Content-Type'] = 'text/html'
        self.headers['Content-Length'] = len(self.body)

    def toString(self):
        resLine = "%s %s %s\r\n" % (self.httpVersion, self.status.code, self.status.msg)
        self.genHeaders()
        resHeaders = ''
        for k, v in self.headers.items():
            resHeaders += "%s: %s\r\n" % (k, v)
        resHeaders += "\r\n"
        resBody = self.body
        string = resLine + resHeaders + resBody
        return string

    def toBytes(self):
        string = self.toString()
        return str2bytes(string)