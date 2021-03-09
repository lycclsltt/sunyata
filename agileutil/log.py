#coding=utf-8

import sys
try:
    from imp import reload
except:
    pass
reload(sys)
try:
    sys.setdefaultencoding('utf-8')
except:
    pass

import logging
from logging.handlers import WatchedFileHandler
from logging import handlers


class Log:

    __slots__ = [
        '__path', '__switch', '__fileHandler', '__logger', '_errorCallBack',
        '_warningCallBack', '_isOutput'
    ]

    __logList = {}
    #__fmt = '%(asctime)s-%(filename)s-%(process)d-%(thread)d-%(funcName)s-[line:%(lineno)d]-%(levelname)s-%(message)s'
    __fmt = '%(asctime)s [%(levelname)s] [p:%(process)d] [t:%(thread)d] [%(threadName)s] %(message)s'
    __shortFmt = '%(asctime)s-%(levelname)s-%(message)s'
    __level = logging.DEBUG
    __instance = None

    def __init__(self, path, isRotate=True, logSaveDays=10, isShortLog=False):
        self.__path = path
        self.__switch = True
        fmter = None
        if isShortLog:
            fmter = logging.Formatter(Log.__shortFmt)
        else:
            fmter = logging.Formatter(Log.__fmt)
        if isRotate:
            self.__fileHandler = handlers.TimedRotatingFileHandler(
                self.__path,
                when='D',
                interval=1,
                backupCount=logSaveDays,
                encoding='utf-8')
        else:
            self.__fileHandler = WatchedFileHandler(self.__path)
        self.__fileHandler.setFormatter(fmter)
        self.__logger = logging.getLogger(path)
        self.__logger.addHandler(self.__fileHandler)
        self.__logger.setLevel(Log.__level)
        self._errorCallBack = None
        self._warningCallBack = None
        self._isOutput = False

    def setOutput(self, tag):
        self._isOutput = tag

    def getOutput(self):
        return self._isOutput

    def setSwitch(self, switch):
        self.__switch = switch

    def getSwitch(self):
        return self.__switch

    def getPath(self):
        return self.__path

    def debug(self, *args):
        logInfo = ' '.join(str(item) for item in args)
        if self.__switch: self.__logger.debug(loginfo)
        if self._isOutput: print(logInfo)

    def info(self, *args):
        logInfo = ' '.join(str(item) for item in args)
        if self.__switch: self.__logger.info(logInfo)
        if self._isOutput: print(logInfo)

    def warning(self, *args):
        logInfo = ' '.join(str(item) for item in args)
        if self.__switch: self.__logger.warning(logInfo)
        if self._isOutput: print(logInfo)
        try:
            if self._warningCallBack: self._warningCallBack(logInfo)
        except:
            pass

    def error(self, *args):
        logInfo = ' '.join(str(item) for item in args)
        if self.__switch: self.__logger.error('\033[31m' + logInfo + "\033[0m")
        if self._isOutput: print('\033[31m' + logInfo + '\033[0m')
        try:
            if self._errorCallBack: self._errorCallBack(logInfo)
        except:
            pass

    def fatal(self, *args):
        logInfo = ' '.join(str(item) for item in args)
        print(logInfo)
        import os
        os._exit(1)

    def setErrorCallBack(self, func):
        self._errorCallBack = func

    def setWarningCallBack(self, func):
        self._warningCallBack = func
