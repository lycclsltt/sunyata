from dataclasses import dataclass, field


@dataclass
class RequestClient(object):
    remoteAddr: str = field(default='')
    port: int = field(default=0)


class HttpRequest(object):

    def __init__(self):
        super().__init__()
        self.method = ''
        self.uri = ''
        self.httpVersion = ''
        self.body = ''
        self.headers = {}
        self.data = {}
        self.scheme = 'http'
        self.queryString = ''
        self.client = RequestClient()


    def setBody(self, body):
        self.body = body