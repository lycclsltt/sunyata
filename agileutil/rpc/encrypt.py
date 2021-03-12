#coding=utf-8

class Encrypt(object):

    PRIVATE_KEY = b'agileutil'

    @classmethod
    def encrypt(cls, bytearr):
        return cls.PRIVATE_KEY + bytearr

    @classmethod
    def unencrypt(cls, bytearr):
        keyLength = len(cls.PRIVATE_KEY)
        if len(bytearr) < keyLength:
            return False, b''
        header = bytearr[:keyLength]
        if header != cls.PRIVATE_KEY:
            return False, b''
        return True, bytearr[keyLength:]