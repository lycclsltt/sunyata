#coding=utf-8

'''
from agileutil.orm import Model, IntField, CharField

#orm init
Model.init('127.0.0.1', 3306, 'root', '', 'test2', min_conn_num=10)


#define a model
class Nation(Model):
    tableName = 'nation' #required
    primaryKey = 'id'    #required
    id = IntField()      #field type int
    name = CharField()   #field type char


#create
nation = Nation(id = 30, name = 'dqdsaw')
nation.create()

#read
obj = Nation.filter('id', '=', 30).get()
print(obj, obj.id, obj.name)
objs = Nation.all()

#update
obj.name = 'hahaha'
obj.update()
obj = Nation.filter('id', '=', 30).get()
print(obj, obj.id, obj.name)

#delete
obj.delete()
obj = Nation.filter('id', '=', 30).first()
print(obj)
'''

from agileutil.db4 import PoolDB
from agileutil.db4 import Orm

class OrmObject(object):

    def __init__(self):
        pass


class OrmModel(OrmObject):
    _connection = None
    tableName = ''
    primaryKey = 'id'

    def __init__(self):
        self.fieldMap = {}

    @classmethod
    def init(cls, host, port, user, passwd, dbName, connect_timeout=10, read_timeout=10, min_conn_num=10,):
        cls._connection = PoolDB(
            host, port, user, passwd, dbName, 
            connect_timeout=connect_timeout, read_timeout=read_timeout, 
            min_conn_num=min_conn_num)
        cls._connection.connect()

    @classmethod
    def getOrm(cls):
        return Orm(cls._connection).table(cls.tableName)

    @classmethod
    def getConnection(cls):
        return cls.getOrm()

    @classmethod
    def getRawConnection(cls):
        return cls._connection


class OrmTypeObject(OrmObject):

    def __init__(self, comment = ''):
        pass

class IntField(OrmTypeObject):
    typeName = 'int'

class CharField(OrmTypeObject):
    typeName = 'char'

class FloatField(OrmTypeObject):
    typeName = 'float'


class Model(OrmModel):

    def __init__(self, **args):
        super().__init__()
        for k, v in args.items():
            if not hasattr(self, k):
                raise Exception('no attr' + str(k))
            self.fieldMap[k] = v

    def create(self):
        return self.getOrm().data(self.fieldMap).insert()

    @classmethod
    def filter(cls, field, cmp, val, raw = False):
        rows = cls.getOrm().where(field, cmp, val).get()
        if raw:
            return rows
        querySet = OrmQuerySet()
        for row in rows:
            obj = cls()
            for k, v in row.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
                obj.fieldMap[k] = v
            querySet.append(obj)
        return querySet

    def update(self):
        data = {}
        for k in self.fieldMap.keys():
            data[k] = getattr(self, k)
        return self.getOrm().data(data).where(self.primaryKey, '=', getattr(self, self.primaryKey)).update()

    def delete(self):
        return self.getOrm().where(self.primaryKey, '=', getattr(self, self.primaryKey)).delete()

    @classmethod
    def all(cls, raw = False):
        rows = cls.getOrm().get()
        if raw:
            return rows
        querySet = OrmQuerySet()
        for row in rows:
            obj = cls()
            for k, v in row.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
                obj.fieldMap[k] = v
            querySet.append(obj)
        return querySet


class OrmQuerySet(Model):
    
    def __init__(self):
        self.set = []
        self.index = 0

    def append(self, elem):
        self.set.append(elem)
        
    def __iter__(self):
        return self

    def __next__(self):
        try:
            elem = self.set[ self.index ]
            self.index = self.index + 1
            return elem
        except:
            raise StopIteration('')

    def objects(self):
        return self.set

    def delete(self):
        for elem in self.set:
            OrmQuerySet.tableName = elem.tableName
            self.getOrm().where(elem.primaryKey, '=', getattr(elem, elem.primaryKey)).delete()

    def first(self):
        if len(self.set) <= 0:
            return None
        return self.set[0]

    def get(self):
        if len(self.set) <= 0:
            raise Exception('no result')
        return self.set[0]

    def count(self):
        return len(self.set)