#coding=utf-8
'''
小表同步
sync_tables(
    '192.168.1.1',
    3306,
    'xxxx',
    'xxxx',
    'db1',

    '192.168.1.2',
    3306,
    'xxxx',
    'xxxx',
    'db1',

    ['users']
)
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from db import DB
import time

SYNC_FAILED_TABLES = []


def get_last_sync_failed_tables():
    return SYNC_FAILED_TABLES


def sync_one_table(src_db, dst_db, table, limit=1000):
    cnt = int(src_db.query('select count(1) from %s' % table)[0]['count(1)'])
    if cnt > limit:
        return False
    create_table_tag = False
    sql = 'show tables'
    rows = dst_db.query(sql)
    if rows == None or len(rows) == 0:
        create_table_tag = True
    else:
        tables = [row.values()[0] for row in rows]
        if table not in tables:
            create_table_tag = True
    if create_table_tag:
        sql = 'show create table %s' % table
        rows = src_db.query(sql)
        if rows == None or len(rows) == 0:
            pass
        else:
            row = rows[0]
            sql = row['Create Table']
            dst_db.query(sql)
    sql = 'select * from %s' % table
    rows = src_db.query(sql)
    if rows == None or len(rows) == 0: return False
    row = rows[0]
    columns = row.keys()
    columns = ','.join(columns)
    sql = "replace into %s(%s) values" % (table, columns)
    for row in rows:
        sql = sql + "('" + "','".join([str(val)
                                       for val in row.values()]) + "'),"
    sql = sql[:-1]
    dst_db.update(sql)
    return True


def sync_tables(src_db_host,
                src_db_port,
                src_db_user,
                src_db_pwd,
                src_db_name,
                dst_db_host,
                dst_db_port,
                dst_db_user,
                dst_db_pwd,
                dst_db_name,
                tables=[],
                sleep_intval=0.01,
                limit=1000):
    '''
    小表的同步
    '''
    if tables == None:
        return False

    global SYNC_FAILED_TABLES
    SYNC_FAILED_TABLES = []

    src_db = DB(src_db_host, src_db_port, src_db_user, src_db_pwd, src_db_name)

    dst_db = DB(dst_db_host, dst_db_port, dst_db_user, dst_db_pwd, dst_db_name)

    all_sync_succed_tag = True

    for table in tables:
        time.sleep(sleep_intval)
        tag = sync_one_table(src_db, dst_db, table, limit)
        if tag == False:
            all_sync_succed_tag = False
            SYNC_FAILED_TABLES.append(table)

    return all_sync_succed_tag
