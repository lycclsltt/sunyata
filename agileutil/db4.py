# coding=utf-8
'''
pip install pymysql
支持数据库连接池的全新版本
'''

import pymysql
from DBUtils.PooledDB import PooledDB

import sys
if sys.version[0:1] == '3': unicode = str


class PoolDB(object):
    def __init__(self,
                 host,
                 port,
                 user,
                 passwd,
                 dbName,
                 log=None,
                 connect_timeout=10,
                 read_timeout=None,
                 min_conn_num=10,
                 auto_commit = True):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbName = dbName
        self.log = log
        self.connectTimeout = connect_timeout
        self.readTimeout = read_timeout
        self.minConnNum = min_conn_num
        self.charset = 'utf8'
        self.pool = None

    def connect(self):
        if self.pool == None:
            self.pool = PooledDB(pymysql,
                                 self.minConnNum,
                                 host=self.host,
                                 port=self.port,
                                 user=self.user,
                                 passwd=self.passwd,
                                 db=self.dbName,
                                 charset=self.charset,
                                 connect_timeout=self.connectTimeout,
                                 read_timeout=self.readTimeout)
            print('PoolDB init finish')

    def close(self):
        if self.pool != None:
            self.pool.close()
            self.pool = None

    def query(self, sql):
        conn = self.pool.connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        conn.close()
        return res

    def update(self, sql):
        conn = self.pool.connection()
        cur = conn.cursor()
        effect_rows = cur.execute(sql)
        conn.commit()
        lastrowId = cur.lastrowid
        cur.close()
        conn.close()
        return effect_rows, lastrowId


class Orm:

    ORDER_ASC = 'asc'
    ORDER_DESC = 'desc'

    def __init__(self, agileutilDb):
        self.db = agileutilDb
        self.tableName = ''
        self.whereCon = ''
        self.updateData = None
        self.fields = []
        self.raw = ''

    def table(self, tableName):
        self.tableName = tableName
        return self

    def field(self, field_name):
        tmpFields = list(set( [ item.strip() for item in field_name.split(',') ] ))
        for tf in tmpFields:
            self.fields.append(tf)
        self.fields = list(set(self.fields))
        return self

    def sql(self, raw):
        self.raw = raw
        return self

    def where(self, *args):
        colName = ''
        data = ''
        compareTag = ''

        if len(args) == 0:
            return self
        elif len(args) == 1:
            if self.whereCon != '':
                self.whereCon = self.whereCon + ' and %s ' % (args[0])
            else:
                self.whereCon = ' where %s ' %  (args[0])
            return self
        elif len(args) == 2:
            compareTag = '='
            colName = args[0]
            data = args[1]
            if '__in' in colName:
                compareTag = 'in'
                colName = colName.replace('__in', '')
                if type(data) == list:
                    itemList = [ "'" + str(item) + "'" for item in data ]
                    data = '(' + ','.join(itemList) + ')'
                elif type(data) == str:
                    splitList = data.split(',')
                    itemList = [ "'" + str(item).strip() + "'" for item in splitList ]
                    data = '(' + ','.join(itemList) + ')'

        elif len(args) == 3:
            colName = args[0]
            compareTag = args[1]
            data = args[2]
        else:
            raise Exception('where param length not support')

        if self.whereCon != '':
            self.whereCon = self.whereCon + ' and `%s` %s' % (colName,
                                                              compareTag)
        else:
            self.whereCon = ' where `%s` %s' % (colName, compareTag)

        if (type(data) == int) or (type(data) == float):
            self.whereCon = self.whereCon + " %s " % data
        else:
            if compareTag == 'in':
                self.whereCon = self.whereCon + " %s " % data
            else:
                data = pymysql.escape_string(data)
                self.whereCon = self.whereCon + " '%s' " % data

        return self

    def orWhere(self, *args):
        colName = ''
        data = ''
        compareTag = ''

        if len(args) == 0:
            return self
        elif len(args) == 1:
            if self.whereCon != '':
                self.whereCon = self.whereCon + ' or %s ' % (args[0])
            else:
                self.whereCon = ' where %s ' %  (args[0])
            return self
        elif len(args) == 2:
            compareTag = '='
            colName = args[0]
            data = args[1]
            if '__in' in colName:
                compareTag = 'in'
                colName = colName.replace('__in', '')
                if type(data) == list:
                    itemList = [ "'" + str(item) + "'" for item in data ]
                    data = '(' + ','.join(itemList) + ')'
                elif type(data) == str:
                    splitList = data.split(',')
                    itemList = [ "'" + str(item).strip() + "'" for item in splitList ]
                    data = '(' + ','.join(itemList) + ')'

        elif len(args) == 3:
            colName = args[0]
            compareTag = args[1]
            data = args[2]
        else:
            raise Exception('where param length not support')

        if self.whereCon != '':
            self.whereCon = self.whereCon + ' or `%s` %s' % (colName,
                                                              compareTag)
        else:
            self.whereCon = ' where `%s` %s' % (colName, compareTag)

        if (type(data) == int) or (type(data) == float):
            self.whereCon = self.whereCon + " %s " % data
        else:
            if compareTag == 'in':
                self.whereCon = self.whereCon + " %s " % data
            else:
                data = pymysql.escape_string(data)
                self.whereCon = self.whereCon + " '%s' " % data

        return self


    def andWhere(self, *args):
        return self.where(*args)

    def getSql(self, cmd):
        #cmd 'insert, delete, update, select'
        if self.raw != '':
            return self.raw
        
        sql = ''
        if cmd == 'select':
            field_str = '*'
            if len(self.fields) == 0:
                field_str = '*'
            else:
                if len(self.fields) == 1:
                    if self.fields[0] == '' or self.fields[0] == '*':
                        field_str = '*'
                    else:
                        field_str = ','.join([ '`' + colname + '`' for colname in self.fields ])
            sql = 'select %s from %s %s' % (field_str, self.tableName, self.whereCon)
        if cmd == 'insert':
            sql_list = []
            if type(self.updateData) == list:
                sql = 'insert into `%s`' % self.tableName
                for row in self.updateData:
                    cols = []
                    for k, v in row.items():
                        cols.append("`" + k + "`")
                    col = ','.join(cols)
                    sql = sql + '(' + col + ') values'
                    break

                values = []
                for row in self.updateData:
                    tup = []
                    for k, v in row.items():
                        if type(v) == int or type(v) == float:
                            tup.append(str(v))
                        elif type(v) == str or type(v) == unicode:
                            tup.append("'" + v + "'")
                    tupStr = '(' + ','.join(tup) + ')'
                    values.append(tupStr)
                valueStr = ', '.join(values)
                sql = sql + valueStr
                self.whereCon = ''
                return sql
            if type(self.updateData) == dict:
                cols = []
                for k, v in self.updateData.items():
                    cols.append("`" + k + "`")
                sql = 'insert into %s' % (self.tableName) + '(' + ','.join(
                    cols) + ') values('
                for k, v in self.updateData.items():
                    if type(v) == int or type(v) == float:
                        sql = sql + str(v) + ','
                    if type(v) == str or type(v) == unicode:
                        sql = sql + "'" + v + "',"
                sql = sql[0:-1]
                sql = sql + ')'
                self.whereCon = ''
                return sql
        if cmd == 'delete':
            sql = """delete from %s %s""" % (self.tableName, self.whereCon)
        if cmd == 'update':
            sql = "update %s set" % (self.tableName)
            for k, v in self.updateData.items():
                if type(v) == int:
                    sql = sql + """ %s=%s,""" % ("`" + k + "`", v)
                if type(v) == str:
                    sql = sql + """ %s='%s',""" % ("`" + k + "`", v)
            sql = sql[0:-1]
            sql = sql + ' ' + self.whereCon
        if cmd == 'count':
            sql = """select count(*) as cnt from %s %s""" % (self.tableName,
                                                             self.whereCon)

        self.whereCon = ''
        return sql

    def data(self, updateData):
        if type(updateData) == list:
            for i in range(len(updateData)):
                for k, v in updateData[i].items():
                    if type(v) == str:
                        updateData[i][k] = pymysql.escape_string(v)
        elif type(updateData) == dict:
            for k, v in updateData.items():
                if type(v) == str:
                    updateData[k] = pymysql.escape_string(v)
        else:
            pass
        self.updateData = updateData
        return self

    def get(self):
        sql = self.getSql('select')
        return self.db.query(sql)

    def values(self, field_name):
        rows = self.get()
        ret = []
        if rows != None:
            for row in rows:
                ret.append(row.get(field_name))
        return ret

    def first(self):
        rows = self.get()
        if len(rows) > 0:
            row = rows[0]
            return row
        return None

    def update(self, retSql=False):
        sql = self.getSql('update')
        return self.db.update(sql)

    def insert(self):
        sql = self.getSql('insert')
        self.db.update(sql)

    def delete(self):
        sql = self.getSql('delete')
        return self.db.update(sql)

    def count(self):
        sql = self.getSql('count')
        rows = self.db.query(sql)
        try:
            row = rows[0]
            num = int(row['cnt'])
        except:
            num = len(rows)
        return num

    def limit(self, limitNum, endpos = None):
        if not str(limitNum).isdigit():
            raise Exception('param limit is not a number')
        if '.' in str(limitNum):
            raise Exception('param limit is not a integer, but a float')
        limitNum = int(limitNum)
        if limitNum < 0: raise Exception('param limit < 0')
        self.whereCon = self.whereCon + " limit %s" % limitNum

        if type(endpos) == int or type(endpos) == str:
            if not str(endpos).isdigit():
                raise Exception('param limit is not a number')
            if int(endpos) < 0 or '.' in str(endpos):
                raise Exception('param limit is invalid')
            self.whereCon = self.whereCon + ", " + str(endpos)

        return self

    def orderBy(self, colName, order=ORDER_ASC):
        if order not in ['asc', 'desc', 'ASC', 'DESC']:
            raise Exception('order by order is invalid')
        self.whereCon = self.whereCon + " order by `%s` %s" % (colName, order)
        return self


class DBCluster(object):
    def __init__(self, masterDb, slaveDbList=[]):
        self._masterDb = masterDb
        self._slaveDbList = slaveDbList
        self._slaveDbCount = len(slaveDbList)
        self._curSlave = 0

    def query(self, sql):
        if len(self._slaveDbList) == 0:
            return self._masterDb.query(sql)
        self._curSlave = self._curSlave + 1
        slaveIndex = self._curSlave % self._slaveDbCount
        slaveDb = self._slaveDbList[slaveIndex]
        return slaveDb.query(sql)

    def queryInstance(self):
        self._curSlave = self._curSlave + 1
        slaveIndex = self._curSlave % self._slaveDbCount
        return slaveIndex

    def update(self, sql):
        return self._masterDb.update(sql)


class DBProxy(object):
    def __init__(self, masterDb, slaveDbList=[]):
        self._masterDb = masterDb
        self._slaveDbList = slaveDbList
        self._slaveDbCount = len(slaveDbList)
        self._curSlave = 0

    def query(self, sql):
        if len(self._slaveDbList) == 0:
            return self._masterDb.query(sql)
        self._curSlave = self._curSlave + 1
        slaveIndex = self._curSlave % self._slaveDbCount
        slaveDb = self._slaveDbList[slaveIndex]
        return slaveDb.query(sql)

    def queryInstance(self):
        self._curSlave = self._curSlave + 1
        slaveIndex = self._curSlave % self._slaveDbCount
        return slaveIndex

    def update(self, sql):
        return self._masterDb.update(sql)

