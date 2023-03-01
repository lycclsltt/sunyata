from sunyata.compress import Compress

class RpcCompress(Compress):

    enableCompressLen = 1024 * 4 #more than 4k enable compress
