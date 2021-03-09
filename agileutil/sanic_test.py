import web
import pymysql
import json
import time
from webpy_base import WebPyBase

#coding=utf-8
from sanic import Sanic
from sanic.response import json, text


class SanicBase:
    def GET(self):
        return text(self.handle())

    def POST(self):
        return text(self.handle())

    def handle(self):
        return 'ok'

    def req(self, k):
        pass


class Test(SanicBase):
    def handle(self):
        print('new req')
        time.sleep(60)
        return 'ok'


urls = ('/intf/test', SanicBase)

if __name__ == '__main__':
    app = Sanic('')
    #for uri, action in urls.items(): app.add_route(action.as_view(), uri)
    for item in [urls[i:i + 2] for i in range(0, len(urls), 2)]:
        app.add_route(item[1].as_view(), item[0])
    app.run(host='0.0.0.0', port=8000, debug=True)
    #web.application(urls, globals()).run()
