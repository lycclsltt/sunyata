# Agileutil

Agileutil is a Python 3 rpc framework that’s written to develop fast. It allows the usage of the rpc/http/orm package, which makes your code speedy and includes many commonly used functions. Agileutil aspires to be simple.

## Install
```
pip install agileutil
```

## RPC
Agileutil provides a simple RPC call.Its underlying infrastructure is based on TCP and the pickle serialization facility.

### TCP RPC server
```python
from agileutil.rpc.server import TcpRpcServer

def sayHello(name):
    return 'hello ' + name

nationServer = TcpRpcServer('0.0.0.0', 9988, workers=4)
nationServer.regist(sayHello)
nationServer.serve()
```
### TCP RPC client
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988)
resp = c.call(func = 'sayHello', args = ('zhangsan'))
print('resp', resp)
```

### Tornado RPC server
TCP server have two choice, These are TcpRpcServer and TornadoTcpRpcServer.
The TronadoTcpServer class was based on Tornado, a python high-performance net libiary.
```python
from agileutil.rpc.server import TornadoTcpRpcServer

def rows(): 
    return {'name' : 123}

s = TornadoTcpRpcServer('127.0.0.1', 9988)
s.regist(rows)
s.serve()
```

### Tornado RPC client
As same as TcpRpcServer, use TcpRpcClient object.
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988)
resp = c.call(func = 'rows'))
print('resp', resp)
```

### UDP RPC server
If you want to use UDP, just change TcpRpcServer to UdpRpcServer.
```python
from agileutil.rpc.server import UdpRpcServer

def sayHello(name): 
    return 'hello ' + name

s = UdpRpcServer('0.0.0.0', 9988)
s.regist(sayHello)
s.serve()
```
### UDP RPC client
```python
from agileutil.rpc.client import UdpRpcClient
cli = UdpRpcClient('127.0.0.1', 9988)
for i in range(5000):
    resp = cli.call(func = 'sayHello', args =('xiaoming') )
    print(resp)
```

## Service discovery
Currently only Consul based service registration and discovery is supported.Future plans support ETCD.

### Health check
If the server process is Down, The client will make requests to other healthy server instances(This health Check is based on Consul's Check mechanism implementation).

### Quick start
The first step, you need a DiscoveryConfig object to specify Consul's address port and your service name, which needs to be globally unique.

```python
from agileutil.rpc.discovery import DiscoveryConfig

disconf = DiscoveryConfig(
    consulHost = '192.168.19.103',
    consulPort = 8500,
    serviceName = 'test-rpc-server',
    serviceHost = local_ip(),
    servicePort = 9988
)
```
Note:
 - The parameters consulHost and consulPort specify the address and port of consul.

 - The parameter ServiceName is used to mark the service, which should be globally unique. Service registration discovery is implemented by the service name
 - The serviceHost and servicePort parameters specify the address and port for the current server to listen on.You need to ensure that the address and port can be connected by the client.

The second step，the setDiscoverConfig() method needs to be called before the serve() method, as follows:
```python
s = TcpRpcServer('0.0.0.0', 9988)
s.regist(sayHello)
disconf = DiscoveryConfig(
    consulHost = '192.168.19.103',
    consulPort = 8500,
    serviceName = 'test-rpc-server',
    serviceHost = local_ip(),
    servicePort = 9988
)
s.setDiscoverConfig(disconf)
s.serve()
```
### Complete server-side example
```python
from agileutil.rpc.server import TcpRpcServer
from agileutil.rpc.discovery import DiscoveryConfig
from agileutil.util import local_ip

def sayHello(): 
    return 'hello '

s = TcpRpcServer('0.0.0.0', 9988)
s.regist(sayHello)
disconf = DiscoveryConfig(
    consulHost = '192.168.19.103',
    consulPort = 8500,
    serviceName = 'test-rpc-server',
    serviceHost = local_ip(),
    servicePort = 9988
)
s.setDiscoverConfig(disconf)
s.serve()
```

### Complete client-side example 
Initialize a DiscoveryTcpRpcClient object from the DiscoveryConfig object
```python
from agileutil.rpc.client import DiscoveryTcpRpcClient
from agileutil.rpc.discovery import DiscoveryConfig

cli = DiscoveryTcpRpcClient(DiscoveryConfig(consulHost='192.168.19.103', consulPort=8500, serviceName='test-rpc-server'))
for i in range(10):
    resp = cli.call(func = 'sayHello')
    print(resp)
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

## Log

Agileutil provides a thread-safe logging tool.It's very simple to use.
```python
from agileutil.log import Log

logger = Log('./debug.log')
logger.info(123, '456')
logger.warning('warning')
logger.error('error')
```

### Log rotate
The log will be stored for 7 days as follows.One log file is generated per day.
```
logger = Log('./debug.log', logSaveDays=7)
logger.info('info')
```
Of course, you can also force logs not to be rotated.
```
logger = Log('./debug.log', isRotate=False)
logger.info('info')
```

### Error log
By default, ERROR level logs are highlighted in red.
Runtime information is appended to the original log.
```
logger.error('runtimee exception raise')
```