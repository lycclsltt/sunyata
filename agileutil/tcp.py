#coding=utf-8

import socket


class Tcp:
    def __init__(self):
        self.bindAddr = '0.0.0.0'
        self.bindPort = 80
        self.backlog = 10
        self.s = None

    def connect(self, addr, port):
        self.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.connect((addr, port))
        return self.s

    def bind(self):
        self.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.bindAddr, self.bindPort))
        self.s.listen(self.backlog)

    def close(self):
        if self.s != None:
            try:
                self.s.close()
            except:
                pass
            self.s = None

    def recvn(self, n):
        buffer = []
        needRecv = n
        while True:
            bytes = self.s.recv(needRecv)
            if bytes:
                buffer.append(bytes)
            else:
                break
            length = len(bytes)
            needRecv = n - length
            if needRecv == 0: break
        data = ''.join(buffer)
        return data

    def recvall(self):
        buffer = []
        while True:
            bytes = self.s.recv(1024)
            if bytes:
                buffer.append(bytes)
            else:
                break
        data = ''.join(buffer)
        return data

    @staticmethod
    def recv_all(sock):
        buffer = []
        while True:
            bytes = sock.recv(1024)
            if bytes:
                buffer.append(bytes)
            else:
                break
        data = ''.join(buffer)
        return data

    def send(self, data):
        self.s.send(data)
        return len(data)

    def syncIOLoop(self, callback):
        self.bind()
        while True:
            sock, addr = self.s.accept()
            callback(sock, addr)
            try:
                sock.close()
            except:
                pass
