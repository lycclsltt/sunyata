#coding=utf-8

import lz4.block as lb

class Compress(object):

    level = 2

    DEBUG = False

    @classmethod
    def compress(cls, bytearr: bytes):
        print(cls.DEBUG)
        compressed = lb.compress(bytearr)
        if cls.DEBUG:
            print('debug, do compress', 'orig len', len(bytearr), 'compress len', len(compressed))
        return compressed

    @classmethod
    def decompress(cls, bytearr):
        print(cls.DEBUG)
        if cls.DEBUG:
            print('debug, do decompress')
        origin = lb.decompress(bytearr)
        return origin