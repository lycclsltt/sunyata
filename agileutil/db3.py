#coding=utf-8
'''
pip install pymysql
一些旧系统使用，为了兼容保留此文件
'''

import pymysql
from .threadlock import ThreadLock


class DB(object):

    __slots__ = [
        '__host', '__port', '__user', '__passwd', '__dbName', '__conn',
        '__cur', '__ispersist', '__log', '__is_mutex', '__connect_timeout',
        '__read_timeout'
    ]

    def __init__(self,
                 host,
                 port,
                 user,
                 passwd,
                 dbName,
                 ispersist=False,
                 log=None,
                 is_mutex=False,
                 connect_timeout=10,
                 read_timeout=None):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__dbName = dbName
        self.__conn = None
        self.__cur = None
        self.__ispersist = ispersist
        self.__log = log
        self.__is_mutex = is_mutex
        self.__connect_timeout = connect_timeout
        self.__read_timeout = read_timeout

        if (self.__ispersist):
            DB.connect(self)

    def log_error(self, err_info):
        if (self.__log):
            self.__log.error(err_info)

    def connect(self):
        try:
            self.__conn = pymysql.Connect(
                host=self.__host,
                port=self.__port,
                user=self.__user,
                passwd=self.__passwd,
                db=self.__dbName,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=self.__connect_timeout,
                read_timeout=self.__read_timeout)
            self.__cur = self.__conn.cursor()
        except Exception as ex:
            self.log_error('db connect exception: ' + str(ex))
            raise ex

    def close(self):
        try:
            self.__cur.close()
            self.__conn.close()
        except Exception as ex:
            self.log_error('db close exception: ' + str(ex))

    def lastrowid(self):
        return self.__cur.lastrowid

    def lock(self):
        if self.__is_mutex:
            ThreadLock.lock()

    def unlock(self):
        if self.__is_mutex:
            ThreadLock.unlock()

    def update(self, sql):
        self.lock()

        if (not self.__ispersist):
            try:
                self.connect()
            except Exception as ex:
                self.unlock()
                raise ex
        else:
            try:
                self.__conn.ping(True)
            except Exception as ex:
                self.log_error(str(ex))
                try:
                    self.connect()
                except Exception as ex:
                    self.unlock()
                    raise ex

        effect_rows = 0
        try:
            effect_rows = self.__cur.execute(sql)
            self.__conn.commit()
        except Exception as ex:
            self.unlock()
            self.log_error('db update exception: ' + str(ex))
            raise ex

        if (not self.__ispersist):
            try:
                self.close()
            except Exception as ex:
                self.unlock()
                raise ex

        self.unlock()
        return effect_rows

    def query(self, sql):
        self.lock()

        if (not self.__ispersist):
            try:
                self.connect()
            except Exception as ex:
                self.unlock()
                raise ex
        else:
            try:
                self.__conn.ping(True)
            except Exception as ex:
                self.log_error(str(ex))
                try:
                    self.connect()
                except Exception as ex:
                    self.unlock()
                    raise ex

        result = None
        try:
            self.__cur.execute(sql)
            result = self.__cur.fetchall()
            #self.__conn.commit()
        except Exception as ex:
            self.unlock()
            self.log_error('db query exception: ' + str(ex))
            raise ex

        if (not self.__ispersist):
            try:
                self.close()
            except Exception as ex:
                self.unlock()
                raise ex

        self.unlock()
        return result

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


'''
rows = Orm(db).table("service").where("allow_stamp_range", 300).where("is_chec_timestamp", 0).where("id", 1).get()

Orm(db).table("service").data([
    {
        "service_name": "orm7",
        'is_check_ip':0,
    },
    {
        "service_name": "orm8",
        'is_check_ip':0,
    },
]).insert()
'''
'''
Orm(db).table("service").data({
    "service_name": "orm10",
    'is_check_ip':0,
}).insert()
'''
'''
Orm(db).table('service').where("id", 37).delete()
'''


class Orm:

    ORDER_ASC = 'asc'
    ORDER_DESC = 'desc'

    def __init__(self, agileutilDb):
        self.db = agileutilDb
        self.tableName = ''
        self.whereCon = ''
        self.updateData = None

    def table(self, tableName):
        self.tableName = tableName
        return self

    def where(self, *args):
        colName = ''
        data = ''
        compareTag = ''

        if len(args) == 0:
            return self
        elif len(args) == 1:
            raise Exception('where param length must be >= 2')
        elif len(args) == 2:
            compareTag = '='
            colName = args[0]
            data = args[1]
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
            data = pymysql.escape_string(data)
            self.whereCon = self.whereCon + " '%s' " % data

        return self

    """
    def where(self, colName, data):
        if self.whereCon != '':
            self.whereCon = self.whereCon + ' and `%s` =' % colName
        else:
            self.whereCon = ' where `%s` =' % colName
        if type(data) == int:
            self.whereCon = self.whereCon + " %s "  % data
        else:
            data = pymysql.escape_string(data) 
            self.whereCon = self.whereCon + " '%s' " % data
        return self
    """

    def getSql(self, cmd):
        #cmd 'insert, delete, update, select'
        sql = ''
        if cmd == 'select':
            sql = 'select * from %s %s' % (self.tableName, self.whereCon)
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
                        if type(v) == int:
                            tup.append(str(v))
                        elif type(v) == str:
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
                    if type(v) == int:
                        sql = sql + str(v) + ','
                    if type(v) == str:
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
        row = rows[0]
        num = int(row['cnt'])
        return num

    def limit(self, limitNum):
        if not str(limitNum).isdigit():
            raise Exception('param limit is not a number')
        if '.' in str(limitNum):
            raise Exception('param limit is not a integer, but a float')
        limitNum = int(limitNum)
        if limitNum < 0: raise Exception('param limit < 0')
        self.whereCon = self.whereCon + " limit %s" % limitNum
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


'''
from pymongo import MongoClient

class MongoCollection:

    def __init__(self, coll_name, db):
        self._coll_name = coll_name
        self._db = db
        self._coll = self._db[coll_name]

    def add(self, obj):
        effect_num = 0
        obj_type = type(obj)
        if obj_type != list and obj_type != dict: return 0
        to_add_list = []
        if obj_type == list: to_add_list = obj
        else: to_add_list.append(obj)
        for item in to_add_list:
            self._coll.insert(item)
            effect_num = effect_num + 1
        return effect_num

    def delete(self, condition):
        ret = self._coll.remove(condition)
        effect_num = ret['n']
        return effect_num

    def update(self, condition, to_update, multi = True):
        to_update = {"$set" : to_update}
        ret = self._coll.update(condition, to_update, multi= multi)
        effect_num = ret['nModified']
        return effect_num

    def find_one(self, condition):
        return self._coll.find_one(condition)

    def find(self, condition, limit_cnt = -1, skip_cnt = -1):
        rows = []
        if limit_cnt > 0 and skip_cnt > 0:
            rows = [row for row in self._coll.find(condition).limit(limit_cnt).skip(skip_cnt)]
        elif limit_cnt > 0:
            rows = [row for row in self._coll.find(condition).limit(limit_cnt)]
        elif skip_cnt > 0:
            rows = [row for row in self._coll.find(condition).skip(skip_cnt)]
        else:
            rows = [row for row in self._coll.find(condition)]
        return rows

class MongoDB:

    def __init__(self, db_name, conn):
        self._db_name = db_name
        self._conn = conn
        self._db = self._conn[db_name]

    def select_coll(self, collection_name):
        coll = MongoCollection(collection_name, self._db)
        return coll

    def delete_coll(self, coll_name):
        ret = self._db.drop_collection(coll_name)
        return self

class Mongo:

    def __init__(self, host, port = 27017):
        self._host = host
        self._port = port
        self._conn = MongoClient(self._host, self._port)

    def select_db(self, db_name):
        db = MongoDB(db_name, self._conn)
        return db
'''
