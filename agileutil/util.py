import socket

def hostname():
    return socket.gethostname()

def local_ip():
    return socket.gethostbyname(socket.gethostname())

def bytes2str(bytes):
    return str(bytes, encoding = 'utf-8')

def str2bytes(string):
    return string.encode(encoding="utf-8")