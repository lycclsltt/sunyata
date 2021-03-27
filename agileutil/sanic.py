#coding=utf-8
'''

基于高性能sanic框架封装

Usage:

from agileutil.sanic import SanicApp, SanicController

class TestController(SanicController):

    async def handle(self):
        self.logInfo("info")
        self.logError("error")
        self.logWarn("warn")
        port = self.getConfig('PORT', '2000')
        headers = self.headers()
        print('headers:', headers)
        method = self.method()
        print('method:', method)
        queryStr = self.queryString()
        print('queryStr:', queryStr)
        path = self.path()
        print('path:', path)
        print('http version:', self.httpVersion())
        print('body:', self.body())
        print('json:', self.requestJson())
        print('cookies:', self.cookies())
        print('remote_addr:', self.remoteAddr())
        print('form:', self.form())
        print('param1:', self.param('param1'))
        print('param2:', self.param('param2'))
        return str(port)

app = SanicApp(debug=True, worker_num=1, log = './access.log')
app.route('/',  TestController)
app.run()
'''

import uuid
import multiprocessing
from sanic import Sanic
from sanic.response import text, raw
from sanic.views import HTTPMethodView
import ujson
from agileutil.log import Log
try:
    from decouple import config
except:
    pass
import logging
from sanic.log import logger

class SanicController(HTTPMethodView):
    def __init__(self):
        self.req = None
        self.logger = None
        self.paramMap = None
        self.isRaw = False

    async def get(self, req):
        return await self.deal(req)

    async def post(self, req):
        return await self.deal(req)

    async def put(self, req):
        return await self.deal(req)

    async def patch(self, req):
        return await self.deal(req)

    async def delete(self, req):
        return await self.deal(req)

    async def deal(self, req):
        self.req = req
        ret = await self.handle()
        if self.isRaw:
            return raw(ret)
        return text(str(ret))  

    async def handle(self):
        return ''

    def resp(self, errno=0, errmsg='', data=''):
        return ujson.dumps({'errno': errno, 'errmsg': errmsg, 'data': data})

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

    def getConfig(self, key: str, default: str = ''):
        ret = None
        try:
            ret = config(key)
        except:
            ret = default
        return ret

    def headers(self):
        return dict(self.req.headers)

    def method(self):
        return self.req.method

    def queryString(self):
        return self.req.query_string

    def path(self):
        return self.req.path

    def httpVersion(self):
        return self.req.version

    def body(self):
        return self.req.body

    def requestJson(self):
        try:
            return self.req.json
        except:
            return None

    def cookies(self):
        return self.req.cookies

    def remoteAddr(self):
        return self.req.remote_addr

    def form(self):
        return self.req.form

    def param(self, key: str):
        self.initParams()
        if key in self.paramMap:
            return self.paramMap[key]
        return ''

    def initParams(self):
        if self.paramMap == None:
            self.paramMap = {}
            queryStr = self.queryString()
            if queryStr != None and queryStr != '':
                kvList = queryStr.split('&')
                print('kvList:', kvList)
                for item in kvList:
                    k, v = item.split('=')
                    self.paramMap[k] = v
            form = self.form()
            if form != None:
                for k, v in form.items():
                    self.paramMap[k] = v

    def getRequest(self):
        return self.req


class SanicApp(object):
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

    def disableLog(self):
        logger.setLevel(logging.WARNING)

    def initApp(self):
        if self.app == None:
            self.app = Sanic(name='agileutil' + str(uuid.uuid1()))

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
                     workers=self.workerNum,
                     access_log=False)

    def route(self, path, className):
        className.setLogger(self.getLogger())
        self.app.add_route(className.as_view(), path)
