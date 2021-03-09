#coding=utf-8

import multiprocessing
import time


class Worker(object):

    __slots__ = ['_target', '_args', '_proc']

    def __init__(self, target, args):
        self._target = target
        self._args = args
        self._proc = None

    def start(self):
        self._proc = multiprocessing.Process(target=self._target,
                                             args=(self._args, ))
        self._proc.start()

    def stop(self):
        self._proc.terminate()

    def join(self, second):
        self._proc.join(second)

    def terminate(self):
        self._proc.terminate()


def cronMain(params):
    target = params[0]
    args = params[1]
    interval = params[2]
    timeout = params[3]
    while True:
        time.sleep(interval)
        w = Worker(target, (args, ))
        w.start()
        if timeout < 0:
            w.join()
        else:
            w.join(timeout)
        w.terminate()


def execLoop(target, args, interval, timeout=-1):
    if interval <= 0: raise Exception("interval params should be > 0")
    if timeout > 0:
        if interval < timeout: raise Exception("interval < timeout")
    manager = Worker(cronMain, (target, args, interval, timeout))
    manager.start()
