
class HttpRequest(object):

    def __init__(self) -> None:
        super().__init__()
        self.method = ''
        self.uri = ''
        self.httpVersion = ''
        self.body = ''
        self.headers = {}
        self.data = {}