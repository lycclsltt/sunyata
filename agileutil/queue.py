#coding=utf-8
'''
usage:

MemQueue().getInstance().push('1').push('2')
print( MemQueue().getInstance().pop() )
'''

import time


class MemQueue:
    def __init__(self, asyncTag=True):
        self.queue = []
        self.asyncTag = asyncTag

    instance = None

    @classmethod
    def getInstance(cls):
        if cls.instance == None:
            cls.instance = MemQueue()
        return cls.instance

    def push(self, elem):
        self.queue.append(elem)
        return self

    def pop(self):
        elem = None

        if self.asyncTag:
            try:
                elem = self.queue.pop()
            except:
                pass
            return elem

        while 1:
            try:
                elem = self.queue.pop()
            except:
                time.sleep(0.01)
                continue
            return elem

    def count(self):
        return len(self.queue)


class UniMemQueue(MemQueue):
    def __init__(self, asyncTag=True):
        super().__init__(asyncTag)
        self.queue = set()

    @classmethod
    def getInstance(cls):
        if cls.instance == None:
            cls.instance = UniMemQueue()
        return cls.instance

    def push(self, elem):
        self.queue.add(elem)
        return self
