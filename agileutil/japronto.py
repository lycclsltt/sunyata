#coding=utf-8
'''

基于高性能japronto框架封装

Usage:

from agileutil.japronto import JapApp, JapController

class TestController(JapController):
    def handle(self):
        self.logInfo("info")
        self.logError("error")
        self.logWarn("warn")
        port = self.getConfig('PORT1', '2000')
        print('port:', port)
        headers = self.headers()
        print('headers:', headers)
        print('method:',self.method())
        print('query str:', self.queryString())
        print('path:', self.path())
        print('http version:', self.httpVersion())
        print('body:', self.body)
        print('json:', self.requestJson())
        print('cookies:', self.cookies())
        print('remote_addr:', self.remoteAddr())
        print('form:', self.form())
        print('param1:', self.param('param1'))
        print('param2:', self.param('param2'))
        return self.resp(data = [1,2,3])


app = JapApp(port = 9876, debug=True, log = './debug.log', worker_num = 20)
app.route('/test', TestController)
app.run()
'''

import multiprocessing
from japronto import Application
import ujson
from agileutil.log import Log
from decouple import config


class JapController(object):
    def __init__(self):
        self.req = None
        self.logger = None
        self.paramMap = None

    def deal(self, req):
        self.req = req
        ret = self.handle()
        return req.Response(text=ret)

    def handle(self):
        return ''

    def resp(self, errno=0, errmsg='', data=''):
        return ujson.dumps({'errno': errno, 'errmsg': errmsg, 'data': data})

    def requestJson(self):
        try:
            return self.req.json
        except:
            return None

    def method(self):
        return self.req.method

    def queryString(self):
        return self.req.query_string

    def path(self):
        return self.req.path

    def getRequest(self):
        return self.req

    def body(self):
        return self.req.body

    def httpVersion(self):
        return self.req.version

    def cookies(self):
        return self.req.cookies

    def remoteAddr(self):
        return self.req.remote_addr

    def form(self):
        return self.req.form

    def initParams(self):
        if self.paramMap == None:
            self.paramMap = {}
            queryStr = self.queryString()
            if queryStr != None:
                kvList = queryStr.split('&')
                for item in kvList:
                    k, v = item.split('=')
                    self.paramMap[k] = v
            form = self.form()
            if form != None:
                for k, v in form.items():
                    self.paramMap[k] = v

    def param(self, key: str):
        self.initParams()
        if key in self.paramMap:
            return self.paramMap[key]
        return ''

    def getConfig(self, key: str, default: str = ''):
        ret = None
        try:
            ret = config(key)
        except:
            ret = default
        return ret

    def headers(self):
        return self.req.headers

    logger = None

    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger

    @classmethod
    def logInfo(cls, string):
        if cls.logger != None: cls.logger.info(string)

    @classmethod
    def logWarn(cls, string):
        if cls.logger != None: cls.logger.warning(string)

    @classmethod
    def logError(cls, string):
        if cls.logger != None: cls.logger.error(string)


class JapApp(object):
    def __init__(self,
                 host: str = '0.0.0.0',
                 port: int = 9876,
                 debug: bool = True,
                 worker_num: int = multiprocessing.cpu_count(),
                 log: str = '',
                 conf: str = ''):
        self.host = host
        self.port = port
        self.debug = debug
        self.workerNum = worker_num
        self.app = None
        self.log = log
        self.logger = None
        self.initApp()
        self.initLog()

    def initApp(self):
        if self.app == None:
            self.app = Application()

    def initLog(self):
        if self.logger == None and self.log != '':
            self.logger = Log(self.log)

    def getLogger(self):
        self.initLog()
        return self.logger

    def run(self):
        self.initApp()
        self.app.run(host=self.host,
                     port=self.port,
                     debug=self.debug,
                     worker_num=self.workerNum)

    def route(self, path, className):
        className.setLogger(self.getLogger())
        self.app.router.add_route(path, className().deal)
