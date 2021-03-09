#!/usr/bin/env python
#coding=utf-8
'''
pip install pymysql
pip install web.py
'''

import web
import pymysql
import json

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'xxx'
DB_PWD = 'xxxx'
DB_NAME = 'xxx'
DB_CHARSET = 'xxxx'

urls = ('/intf/get_servers_by_rack', 'get_servers_by_rack')


def getConnection():
    conn = pymysql.connect(host=DB_HOST,
                           port=DB_PORT,
                           user=DB_USER,
                           password=DB_PWD,
                           db=DB_NAME,
                           charset=DB_CHARSET,
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


def query(sql):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def update(sql):
    conn = getConnection()
    cursor = conn.cursor()
    effect_row = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return effect_row


def auth(func):
    def wrapper(*args, **kw):
        i = web.input()
        app = i.get('app')
        if app == None or app not in ['test']:
            return web.Forbidden()
        return func(*args, **kw)

    return wrapper


def get(k):
    i = web.input()
    v = ''
    try:
        v = i[k]
    except:
        pass
    return v


class get_servers_by_rack:
    def GET(self):
        return self.REQUEST()

    def POST(self):
        return self.REQUEST()

    def REQUEST(self):
        rackName = get('rack_name')
        if rackName == '': return ''
        sql = "select id from rack_infos where name = '%s'" % (rackName)
        rows = query(sql)
        if rows == None or len(rows) == 0: return ''
        row = rows[0]
        rackId = row['id']
        sql = "select * from servers where rack_id=%s" % (rackId)
        rows = query(sql)
        if rows == None or len(rows) == 0: return ''
        for r in rows:
            r['pandian_time'] = str(r['pandian_time'])
            r['updated_at'] = str(r['updated_at'])
            r['created_at'] = str(r['created_at'])
        return json.dumps(rows)


if __name__ == '__main__': web.application(urls, globals()).run()
'''
sys.argv.append(config('PORT'))
urls = router.routers
app = web.application(urls, globals())
web.config.session_parameters['timeout'] = config('SESSION_EXPIRE', cast=int) 
session = web.session.Session(app, web.session.DiskStore(config('SESSION_PATH')))

def session_hook():
    web.ctx.session = session
    
app.add_processor(web.loadhook(session_hook))
application = app.wsgifunc()

if __name__ == '__main__': 
    app.run()
'''
