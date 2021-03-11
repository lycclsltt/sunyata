#coding=utf-8

class FuncNotFoundException(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg