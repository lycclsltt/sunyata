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


class WebPyBase:
    def render(self, page_dir='static/pages/', encode='utf-8'):
        rend = render_jinja(page_dir, encoding=encode)
        return rend

    def GET(self):
        return self.handle()

    def POST(self):
        return self.handle()

    def handle(self):
        return ''

    def request(self, k):
        i = web.input()
        v = ''
        try:
            v = i[k]
        except:
            pass
        return v.strip()

    def req(self, k):
        return self.request(k)

    def resp(self,
             errno=0,
             errmsg='',
             data='',
             page='',
             pagesize='',
             control_allow='*'):
        try:
            web.header("Access-Control-Allow-Origin", control_allow)
        except:
            pass
        ret = {}
        if platform.python_version_tuple()[0] == '2':
            ret = {'errno': errno, 'errmsg': unicode(errmsg), 'data': data}
        else:
            ret = {'errno': errno, 'errmsg': errmsg, 'data': data}
        if page != '' and pagesize != '':
            ret['page'] = page
            ret['pagesize'] = pagesize
        return ujson.dumps(ret)

    def session(self, k, v=None):
        '''
        init in main application:
        
        def session_hook():
            web.ctx.session = session
        app.add_processor(web.loadhook(session_hook))
        
        '''
        if v == None:
            #get
            v = ''
            try:
                v = web.ctx.session[k]
            except Exception as ex:
                pass
            return v
        else:
            #set
            try:
                web.ctx.session[k] = v
                #print('[session] set %s to %s' % (str(k), str(v)))
            except Exception as ex:
                #print('[session] web.ctx.session[k] = v exception:', ex)

    def kill_session(self):
        web.ctx.session.kill()

    def deny(self, errmsg=u'您没有权限'):
        return self.resp(errno=1, errmsg=errmsg)
