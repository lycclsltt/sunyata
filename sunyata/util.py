import socket

def hostname():
    return socket.gethostname()

def local_ip():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip == '127.0.0.1':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    return ip

def bytes2str(bytes):
    return str(bytes, encoding = 'utf-8')

def str2bytes(string):
    return string.encode(encoding="utf-8")