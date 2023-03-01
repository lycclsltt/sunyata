#coding=utf-8

'''
Usage:

from sunyata.algorithm.trie import TrieNode, Trie
import random
arr = [u'运维', u'运维开发', u'运营']
print('arr', arr)
t = Trie()
for elem in arr:
    t.append(elem)
words = t.getWords()
print(words)
isExists = t.isContains('abcv')
print(isExists)
t.update(u'运维开发', u'运气')
words = t.getWordsByKw('运')
print(words)

'''

class TrieNode(object):
    
    def __init__(self):
        self.char = ''
        self.pre = None
        self.isRoot = False
        self.childMap = {}
        self.data = None
        self.isWordEnd = False
    
    def isLeaf(self):
        if len(self.childMap) <= 0:
            return True
        return False
    
    def isRoot(self):
        return self.isRoot
    
    def childNodes(self):
        nodes = []
        for _, node in (self.childMap).items():
            nodes.append(node)
        return nodes
    
    def hasChild(self):
        childNodes = self.childNodes()
        if len(childNodes) <= 0:
            return False
        return True


class Trie(object):
    
    def __init__(self):
        self.root = TrieNode()
        self.root.isRoot = True
        self.curString = ''
        self.words = []
        
    def getRootNode(self):
        return self.root
    
    def isHasChildNodeByChar(self, node, char):
        if char in node.childMap:
            return True
        return False
        
    def getChildNodeByChar(self, node, char):
        return node.childMap.get(char)
    
    def append(self, string):
        curnode = self.root
        linkstr = ''
        for char in string:
            linkstr = linkstr + char
            if self.isHasChildNodeByChar(curnode, char):
                curnode = self.getChildNodeByChar(curnode, char)
            else:
                childNode = TrieNode()
                childNode.char = char
                childNode.pre = curnode
                childNode.isRoot = False
                childNode.data = linkstr
                curnode.childMap[char] = childNode
                curnode = childNode
        curnode.isWordEnd = True
                
    def getNodeWord(self, node):
        words = []
        if node.isWordEnd:
            words.append(node.data)
        if node.hasChild():
            for childNode in node.childNodes():
                words = words + self.getNodeWord(childNode)
        return words
                
    def getWords(self):
        words = self.getNodeWord(self.root)
        return words
    
    def isContains(self, kw):
        curnode = self.root
        for char in kw:
            if self.isHasChildNodeByChar(curnode, char):
                curnode = self.getChildNodeByChar(curnode, char)
            else:
                return False
        return True
    
    def getWordsByKw(self, kw):
        words = []
        curnode = self.root
        for char in kw:
            if self.isHasChildNodeByChar(curnode, char):
                curnode = self.getChildNodeByChar(curnode, char)
            else:
                return words
        words = self.getNodeWord(curnode)
        return words
    
    def remove(self, string):
        curnode = self.root
        for char in string:
            if self.isHasChildNodeByChar(curnode, char):
                curnode = self.getChildNodeByChar(curnode, char)
            else:
                return
        if curnode.hasChild():
            curnode.isWordEnd = False
            return
        while curnode != self.root:
            if not curnode.hasChild():
                if not curnode.pre.isWordEnd:
                    del curnode.pre.childMap[curnode.char]
                    curnode = curnode.pre
                else:
                    break
            else:
                break
            
    def update(self, string, newstring):
        self.remove(string)
        self.append(newstring)