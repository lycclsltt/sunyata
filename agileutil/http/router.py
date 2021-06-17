
class HttpRouter(object):

    def __init__(self) -> None:
        super().__init__()
        self.path = ''
        self.method = None
        self.func = None

    def getFunc(self):
        return self.func