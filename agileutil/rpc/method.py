import operator
import asyncio

class RpcMethod(object):

    TYPE_WITHOUT_CLASS = 0
    TYPE_WITH_CLASS = 1

    def __init__(self, methodType, method, classDefine = None, isCoroutine = False):
        self._methodType = methodType
        self._method = method
        self._classDefine = classDefine
        self._isCoroutine = isCoroutine
        if self._methodType == self.TYPE_WITH_CLASS and self._classDefine == None:
            raise Exception('classDefine is None')

    def call(self, *args):
        if self._methodType == self.TYPE_WITH_CLASS:
            classInstance = self._classDefine()
            if self._isCoroutine:
                resp = asyncio.run( operator.methodcaller(self._method.__name__, *args)(classInstance) )
            else:
                resp = operator.methodcaller(self._method.__name__, *args)(classInstance)
        else:
            if self._isCoroutine:
                resp = asyncio.run(self._method(*args))
            else:
                resp = self._method(*args)
        return resp

    async def asyncCall(self, *args):
        if self._methodType == self.TYPE_WITH_CLASS:
            classInstance = self._classDefine()
            if self._isCoroutine:
                resp = await ( operator.methodcaller(self._method.__name__, *args)(classInstance) )
            else:
                resp = operator.methodcaller(self._method.__name__, *args)(classInstance)
        else:
            if self._isCoroutine:
                resp = await self._method(*args)
            else:
                resp = self._method(*args)
        return resp