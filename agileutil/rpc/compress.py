#coding=utf-8

from agileutil.compress import Compress

class RpcCompress(Compress):

    enableCompressLen = 1024 * 4 #大于4k开启压缩
