#coding=utf-8
'''
Usage:

h = HashTable()
h.set("a", "1")
h.set("b", "2")
print(len(h))
print(h.get("a"))
h["abc"] = "abc"
print(h["abc"])
print(h.hasKey("a"))
for k, v in h:
    print(k, v)
for k, v in h.items():
    print(k, v)
'''


class HashTable(object):
    def __init__(self, size=99999):
        self.size = size
        self.hashList = [list() for _ in range(size)]

    def set(self, key, value):
        hashKey = hash(key) % self.size
        for item in self.hashList[hashKey]:
            if item[0] == key:
                item[1] = value
                return
        self.hashList[hashKey].append([key, value])

    def get(self, key):
        hashKey = hash(key) % self.size
        for item in self.hashList[hashKey]:
            if item[0] == key:
                return item[1]
        raise KeyError

    def hasKey(self, key):
        try:
            self.get(key)
        except KeyError:
            return False
        return True

    def __len__(self):
        length = 0
        for item in self.hashList:
            length = length + len(item)
        return length

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __iter__(self):
        return self.items()

    def items(self):
        kvList = []
        for item in self.hashList:
            if len(item) > 0:
                kvList = kvList + item
        return iter(kvList)
