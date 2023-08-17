from sunyata.http.factory import HttpFactory
from sunyata.http.status import HttpStatus
import abc


class Middleware(metaclass=abc.ABCMeta):

    def __init__(self):
        self.resetResponse()

    def resetResponse(self):
        self.resp = None

    def abort(self, statusCode, responseText):
        status = HttpStatus()
        status.code = statusCode
        httpResponse = HttpFactory.genHttpResponse(status, responseText)
        self.resp = httpResponse

    @abc.abstractmethod
    def handle(self, request):
        pass