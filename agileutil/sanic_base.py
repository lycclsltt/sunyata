#coding=utf-8

import ujson
import web
from web.contrib.template import render_jinja
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
import platform
from sanic.response import json, text


class SanicBase:
    def GET(self):
        return text(self.handle())

    def POST(self):
        return text(self.handle())

    def handle(self):
        return ''

    def req(self, k):
        pass
