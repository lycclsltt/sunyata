import operator

class RpcMethod(object):

    TYPE_WITHOUT_CLASS = 0
    TYPE_WITH_CLASS = 1

    def __init__(self, methodType, method, classDefine = None):
        self._methodType = methodType
        self._method = method
        self._classDefine = classDefine
        if self._methodType == self.TYPE_WITH_CLASS and self._classDefine == None:
            raise Exception('classDefine is None')

    def call(self, *args):
        if self._methodType == self.TYPE_WITH_CLASS:
            classInstance = self._classDefine()
            resp = operator.methodcaller(self._method.__name__, *args)(classInstance)
            return resp
        resp = self._method(*args)
        return resp