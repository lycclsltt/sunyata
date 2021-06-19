
class HttpRequest(object):

    __slots__ = ('method', 'uri', 'httpVersion', 'body', 'headers', 'data')

    def __init__(self) -> None:
        super().__init__()
        self.method = ''
        self.uri = ''
        self.httpVersion = ''
        self.body = ''
        self.headers = {}
        self.data = {}

    def setBody(self, body):
        self.body = body