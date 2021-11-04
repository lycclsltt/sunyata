import lz4.block as lb

class Compress(object):

    level = 3

    DEBUG = False

    @classmethod
    def compress(cls, bytearr: bytes):
        compressed = lb.compress(bytearr)
        if cls.DEBUG:
            print('debug, do compress', 'orig len', len(bytearr), 'compress len', len(compressed))
        return compressed

    @classmethod
    def decompress(cls, bytearr):
        if cls.DEBUG:
            print('debug, do decompress')
        origin = lb.decompress(bytearr)
        return origin