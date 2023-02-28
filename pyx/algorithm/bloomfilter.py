#coding=utf-8
'''
Usage:
bloom_filter = BloomFilter()
urls = ['www.baidu.com','mathpretty.com','sina.com']
urls_check = ['mathpretty.com','zhihu.com', 'sina.com', 'ali.com']
for url in urls: bloom_filter.add(url)
for url_check in urls_check:
    result = bloom_filter.contains(url_check)
    print('url : ',url_check,' contain : ',result)
'''

import crypt


class BloomFilter(object):
    def __init__(self, bitsize=30000):
        self.bitarr = [0 for _ in range(bitsize)]
        self.bitsize = bitsize

    def getPosList(self, string):
        posList = []
        for salt in ['41', '42', '43', '44', '45']:
            cryStr = crypt.crypt(string, salt)
            pos = hash(cryStr) % self.bitsize
            posList.append(pos)
        return posList

    def add(self, string):
        posList = self.getPosList(string)
        for pos in posList:
            self.bitarr[pos] = 1

    def contains(self, string):
        posList = self.getPosList(string)
        for pos in posList:
            if self.bitarr[pos] != 1:
                return False
        return True
