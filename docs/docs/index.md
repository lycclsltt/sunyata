# Agileutil

Agileutil is a Python 3 rpc framework that’s written to develop fast. It allows the usage of the rpc/http/orm package, which makes your code speedy and includes many commonly used functions. Agileutil aspires to be simple.

## Install
```
pip install agileutil
```

## RPC
Agileutil provides a simple RPC call.Its underlying infrastructure is based on TCP and the pickle serialization facility.

### Rpc server
```python
from agileutil.rpc.server import TcpRpcServer

def sayHello(name):
    return 'hello ' + name

nationServer = TcpRpcServer('0.0.0.0', 9988, workers=4)
nationServer.regist(sayHello)
nationServer.serve()
```
### Rpc client
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988)
resp = c.call(func = 'sayHello', args = ('zhangsan'))
print('resp', resp)
```

## ORM
Define a table named Nation with two filed: id(int, promary key) and name(varchar).
```python
CREATE TABLE `nation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
```
First call Model.init() method and set min_conn_num param's value for database connection pool,
then define a class which was extend Model class.
```python
from agileutil.orm import Model, IntField, CharField

Model.init('127.0.0.1', 3306, 'root', '', 'test2', min_conn_num=10)

class Nation(Model):
    tableName = 'nation' #required
    primaryKey = 'id'    #required
    id = IntField()      #field type int
    name = CharField()   #field type char
```
### Create
```python
Nation(name='test').create()
```
### Read one
```python
obj = Nation.filter('name', '=', 'test').first()
print(obj.name, obj.id)
```
### Read list
```python
objs = Nation.filter('name', '=', 'test')
for obj in objs: print(obj.name, obj.id)
```
### Update
```python
obj = Nation.filter('name', '=', 'test').first()
obj.name = 'test update'
obj.update()
```
### Delete
```python
Nation.filter('name', '=', 'test').delete()
```
Delete by object
```python
obj = Nation.filter('name', '=', 'test').first()
obj.delete()
```

## PoolDB
PoolDB is a database connection pool class.It is easy to use.ORM function was developed base on PoolDB.
If you want to do CRUD on database without orm, you can use this class.

### Define PoolDB object.
```python
from agileutil.db4 import PoolDB
db = PoolDB(host='127.0.0.1', port=3306, user='root', passwd='', dbName='test2', min_conn_num=10)
db.connect()
```
### Search
```python
sql = 'select * from nation'
rows = db.query(sql)
print(rows)
```
### Update (include delete, update, create)
```python
sql = "insert into nation(name) values('test')"
effect, lastid = db.update(sql)
print(effect,lastid)

sql = "delete from nation where name='test'"
effect, _ = db.update(sql)
print(effect,lastid)
```

## DB
DB is a database class without connection pool.Its use is similar to that of PoolDB.
### Define DB object.
```python
from agileutil.db import DB
db = DB(host='127.0.0.1', port=3306, user='root', passwd='', dbName='test2')
```
### Search
```python
sql = 'select * from nation'
rows = db.query(sql)
print(rows)
```
### Update (include delete, update, create)
```python
sql = "insert into nation(name) values('test')"
effetc = db.update(sql)
print(effetc, db.lastrowid())
```