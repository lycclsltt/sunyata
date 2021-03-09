#coding=utf-8

import time


class MemValue:
    def __init__(self, value='', ttl=-1):
        self.value = value
        self.createStamp = time.time()
        self.ttl = ttl

    def isExpire(self):
        if self.ttl == -1:
            return False
        now = time.time()
        diff = now - self.createStamp
        if diff >= self.ttl:
            return True
        return False


class MemStringCache:

    instance = None

    def __init__(self):
        self.data = {}

    @classmethod
    def getInstance(cls):
        if cls.instance == None:
            cls.instance = MemStringCache()
        return cls.instance

    def set(self, k, v, ttl=-1):
        self.data[k] = MemValue(value=v, ttl=ttl)

    def get(self, k):
        if k not in self.data:
            return None
        memVal = self.data[k]
        if memVal.isExpire():
            del self.data[k]
            return None
        return memVal.value

    def count(self):
        cnt = 0
        for k in self.data.keys():
            v = self.get(k)
            if v == None:
                continue
            cnt = cnt + 1
        return cnt
