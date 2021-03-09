#coding=utf-8

import threading


class ThreadLock(object):
    """
    mutex lock
    """

    __threadLock = threading.Lock()

    @staticmethod
    def lock():
        ThreadLock.__threadLock.acquire()

    @staticmethod
    def unlock():
        ThreadLock.__threadLock.release()
