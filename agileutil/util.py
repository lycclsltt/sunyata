import socket

def hostname():
    return socket.gethostname()

def local_ip():
    return socket.gethostbyname(socket.gethostname())