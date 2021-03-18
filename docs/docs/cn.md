# Agileutil

### 文档
[英文文档](docs/docs/index.md)

Agileutil是一个Python3+ RPC框架。提供了rpc/http/orm/log等通用功能，提供了微服务相关的底层服务，使开发者专注于业务开发。

## 安装
```
pip install agileutil
```

## RPC

基于TCP协议和Pickle序列化方式实现的远程调用。下面是一个基于TCP协议的服务端例子。
- 创建一个TcpRpcServer对象, 指定监听端口和地址
- 调用regist()方法，将提供服务的方法注册到服务端
- 调用serve()方法，开始处理客户端请求

### TCP RPC 服务端
```python
from agileutil.rpc.server import TcpRpcServer

def sayHello(name):
    return 'hello ' + name

nationServer = TcpRpcServer('0.0.0.0', 9988, workers=4)
nationServer.regist(sayHello)
nationServer.serve()
```
### TCP RPC 客户端
客户端例子：
- 创建TcpRpcClient对象，指定RPC服务端地址
- 通过call()方法，指定服务端方法名称和参数
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988)
resp = c.call(func = 'sayHello', args = ('zhangsan'))
print('resp', resp)
```

### Tornado RPC 服务端
TornadoTcpRpcServer同样是基于TCP协议的RPC服务端，只是底层是基于Tornado高性能网络库实现。你同样可以使用上面例子中的TcpRpcServer(一个基于多线程的并发服务器)
```python
from agileutil.rpc.server import TornadoTcpRpcServer

def rows(): 
    return {'name' : 123}

s = TornadoTcpRpcServer('127.0.0.1', 9988)
s.regist(rows)
s.serve()
```

### Tornado RPC 客户端
客户端仍然使用TcpRpcClient对象。
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988)
resp = c.call(func = 'rows'))
print('resp', resp)
```

### UDP RPC 服务端
如果想要使用UDP协议，将TcpRpcServer替换为UdpRpcServer即可。一个UDP RPC服务端的例子如下，与TCP类似：
- 创建UdpRpcServer对象，指定监听的地址和端口
- 调用regist()方法，将需要被客户端请求的方法注册进去
- 调用serve()方法开始处理客户端请求
- 返回的内容和调用本地方法没有差别，框架内部通过序列化和反序列化，将数据转化为程序内的对象（字典、列表、内置类型、各种类对象等等）
```python
from agileutil.rpc.server import UdpRpcServer

def sayHello(name): 
    return 'hello ' + name

s = UdpRpcServer('0.0.0.0', 9988)
s.regist(sayHello)
s.serve()
```
### UDP RPC 客户端
一个UDP客户端的例子：
- 创建UdpRpcClient对象，指定服务端地址和端口
- 调用call()方法，并指定服务端的方法名称和参数
- 返回的内容和调用本地方法没有差别，框架内部通过序列化和反序列化，将数据转化为程序内的对象（字典、列表、内置类型、各种类对象等等）
```python
from agileutil.rpc.client import UdpRpcClient
cli = UdpRpcClient('127.0.0.1', 9988)
for i in range(5000):
    resp = cli.call(func = 'sayHello', args =('xiaoming') )
    print(resp)
```

## 服务发现
Agileutil既支持客户端与服务端直连，也支持服务注册发现。
目前仅支持基于Consul的服务发现。未来计划支持etcd。


### 监控检查
基于Consul的Check机制。服务注册后，自动添加一个定期的健康检查（默认为TCP端口检查，未来计划支持HTTP健康检查）。一旦服务进程挂掉，那么客户端将请求到其他健康的服务节点上。同时客户端也存在重试机制（由于健康检查存在时间间隔，可能服务端进程挂掉后，仍需等待一段时间才被Consul发现，这时客户端如果请求到挂掉的服务节点上失败后，客户端会尝试请求其他服务节点进行重试）。

### 快速开始
第一步，你需要定义一个DiscoverConfig对象。
指定用于服务注册发现的Consul的地址和端口。同时通过serviceName参数指定一个全局唯一的服务名称（用于标记服务端服务）。并同时指定服务端监听的地址和端口。

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
说明:
 - consulHost 和 consulPort 参数指定Consul的地址和端口
 - ServiceName 参数用于标记服务端名称，并通过服务名称进行服务发现，需要保证全局唯一
 - serviceHost和servicePort参数指定服务端监听的端口和地址


第二步、调用setDiscoverConfig()方法将DiscoveryConfig对象传入，之后调用serve()方法，开始处理请求
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
### 完整的服务端示例
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

### 完整的客户端示例 
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
定义一个nation表，包含两个字段：id字段和name字段
```python
CREATE TABLE `nation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
```
- 首先调用Model.init()方法，设置mysql连接地址等信息
- 然后为nation表定一个Nation类，并继承自Model类
- 指定字段类型
```python
from agileutil.orm import Model, IntField, CharField

Model.init('127.0.0.1', 3306, 'root', '', 'test2', min_conn_num=10)

class Nation(Model):
    tableName = 'nation' #required
    primaryKey = 'id'    #required
    id = IntField()      #field type int
    name = CharField()   #field type char
```
### 创建记录
```python
Nation(name='test').create()
```
### 查询一条记录
```python
obj = Nation.filter('name', '=', 'test').first()
print(obj.name, obj.id)
```
### 查询多条记录
```python
objs = Nation.filter('name', '=', 'test')
for obj in objs: print(obj.name, obj.id)
```
### 修改记录
```python
obj = Nation.filter('name', '=', 'test').first()
obj.name = 'test update'
obj.update()
```
### 删除记录
```python
Nation.filter('name', '=', 'test').delete()
```
另一种删除的方式
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

## Thanks
[![Stargazers repo roster for @lycclsltt/agileutil](https://reporoster.com/stars/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/stargazers)

[![Forkers repo roster for @lycclsltt/agileutil](https://reporoster.com/forks/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/network/members)