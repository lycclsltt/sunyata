class HttpRouter(object):

    __slots__ = ('path', 'methods', 'func')

    def __init__(self) -> None:
        super().__init__()
        self.path = ''
        self.methods = None
        self.func = None

    def getFunc(self):
        return self.func