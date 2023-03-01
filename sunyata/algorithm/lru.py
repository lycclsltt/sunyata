#coding=utf-8
'''
Usage:


lru = LRUCache(size = 10)
for i in range(10):
    key = str(i)
    lru.put(key, key) 
lru.dump()
for i in range(5):
    lru.get(str(i))
lru.dump()
for k, v in lru.items():
    print(k, v)
'''

import collections


class Node(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class LinkNode(object):
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, node):
        if self.head == None and self.tail == None:
            node.next = None
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            node.next = None
            self.tail = node
        self.length = self.length + 1

    def dump(self):
        node = self.head
        while node != None:
            print(node.key, node.value)
            node = node.next
        print('---------------------')

    def items(self):
        kvList = []
        node = self.head
        while node != None:
            kvList.append([node.key, node.value])
            node = node.next
        return iter(kvList)

    def find(self, key):
        node = self.head
        while node != None:
            if node.key == key:
                return node
            node = node.next
        return None

    def appendHead(self, node):
        node.next = self.head
        if self.head == None and self.tail == None:
            self.tail = node
        self.head = node
        self.length = self.length + 1

    def removeTail(self):
        if self.tail == None: return
        preNode = self.head
        curNode = self.head
        while 1:
            if curNode != self.tail:
                preNode = curNode
                curNode = curNode.next
            else:
                break
        preNode.next = None
        self.tail = preNode
        self.length = self.length - 1

    def removeNode(self, node):
        if self.head == None and self.tail == None:
            return
        if self.head == node:
            self.head = node.next
            self.length = self.length - 1
            return
        if self.tail == node:
            self.removeTail()
            return
        preNode = curNode = self.head
        while curNode != self.tail:
            if curNode.key == node.key:
                preNode.next = node.next
                self.length = self.length - 1
                return
            preNode = curNode
            curNode = curNode.next


class LRUCache(object):
    def __init__(self, size=9999):
        self.size = size
        self.link = LinkNode()

    def get(self, key):
        node = self.link.find(key)
        if node != None:
            self.link.removeNode(node)
            self.link.appendHead(node)
        else:
            raise KeyError

    def put(self, key, value):
        node = self.link.find(key)
        if node != None:
            self.link.removeNode(node)
            self.link.appendHead(node)
        else:
            node = Node(key, value)
            if (self.link.length + 1) <= self.size:
                self.link.appendHead(node)
            else:
                self.link.appendHead(node)
                self.link.removeTail()
        return self

    def length(self):
        return self.link.length

    def dump(self):
        return self.link.dump()

    def items(self):
        return self.link.items()
