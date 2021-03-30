中文 | [English](docs/docs/en.md)

# Agileutil

Agileutil是一个Python3 RPC框架。基于微服务架构，封装了rpc/http/orm/log等常用组件，提供了简洁的API，开发者可以很快上手，快速进行业务开发。


## 版本要求
Python >= 3.6


## 安装
```
pip install agileutil
```

## RPC

这是Agileutil最核心的功能。基于TCP协议和Pickle序列化方式实现的远程过程调用。下面是一个基于TCP协议的服务端例子。可参考下面的步骤进行开发：
- 创建一个TcpRpcServer对象, 指定服务端监听地址和端口
- 通过@rpc装饰器注册需要被客户端请求的方法
- 调用serve()方法，开始处理客户端请求

### TCP RPC 服务端
```python
from agileutil.rpc.server import TcpRpcServer
from agileutil.rpc import rpc

@rpc
def sayHello(name):
    return 'hello ' + name

nationServer = TcpRpcServer('0.0.0.0', 9988, workers=4)
nationServer.serve()
```
> 除了使用@rpc注册方法，还可以使用regist()方法，参考下面的例子
``` python
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
- 通过call()方法，指定服务端方法名称和参数（注意：如果方法名不存在，或者服务端未调用regist()方法注册，那么call（）方法将抛出异常）
- call() 方法的返回值和在本地调用一样，原来是什么返回类型，就还是什么（例如返回字典、列表、对象甚至内置类型，经过序列化后，不会发生改变）
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988, timeout=5)
resp = c.call(func = 'sayHello', args = 'zhangsan') #或resp = c.call(func = 'sayHello', args = ('zhangsan', ） )
print('resp', resp)
```

### 指定多个服务端地址
- 通过servers参数，你也可以创建一个指定多个服务端地址的client对象，默认采用轮询的负载均衡策略，将请求转发到多个server上，如果请求其中一个server出现了失败，那么会自动重试。框架中所有TCP/UDP/HTTP的client都支持servers参数，都可以指定多个服务端地址，参考下面的例子:
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient(servers = ['127.0.0.1:9988', '127.0.0.1:9989'])
resp = c.call(func = 'sayHello', args = 'zhangsan')
print('resp', resp)
```
> 注意：
> 如果通过servers参数指定了多个服务端地址，又同时指定了服务发现的consul地址，那么实际请求的服务端节点是由server参数决定的，所以使用时请注意不要和服务发现同时使用。


### Tornado RPC 服务端
TornadoTcpRpcServer同样是基于TCP协议的RPC服务端，只是底层是基于Tornado高性能网络库实现。你同样可以使用TornadoTcpRpcServer创建一个TCP服务，参考TcpRpcServer的创建步骤：
- 创建一个TornadoTcpRpcServer对象，指定监听的地址和端口
- 调用regist()注册需要提供给客户端的方法
- 调用server()方法开始处理客户端请求

```python
from agileutil.rpc.server import TornadoTcpRpcServer

def rows(): 
    return {'name' : 123}

s = TornadoTcpRpcServer('127.0.0.1', 9988)
s.regist(rows)
s.serve()
```

### Tornado RPC 客户端
客户端使用TcpRpcClient对象即可。
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient('127.0.0.1', 9988)
resp = c.call(func = 'rows'))
print('resp', resp)
```

### HTTP RPC 服务端
Agileutil也提供了基于HTTP协议的远程过程调用。底层是基于高性能的Sanic异步web框架实现的，使用起来非常简单，和TcpRpcServer的用法类似:
```python
from agileutil.rpc.server import HttpRpcServer

def sayHello(name):
    return 'hello ' + name

s = HttpRpcServer('0.0.0.0', 9988, workers=1)
s.regist(sayHello)
s.serve()
```

### HTTP RPC Client
同样的，客户端使用对应的HttpRpcClient对象:
```python
from agileutil.rpc.client import HttpRpcClient

cli = HttpRpcClient('127.0.0.1', 9988)
for i in range(10):
    resp = cli.call(func = 'sayHello', args=('zhangsan', ))
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
    resp = cli.call(func = 'sayHello', args = 'xiaoming' )
    print(resp)
```

## 数据压缩
Agileutil默认采用lz4进行压缩、解压缩（经过测试，它的压缩效果和gzip, zlib比较接近，压缩、解压缩性能是zlib的10倍左右）。
在数据传输大于4KB时，自动开启进行压缩。对端根据一个标记位进行判断，自动进行解压缩处理（或不处理，未经过压缩的情况）。开发者无需关心
数据的压缩、解压缩过程，经过测试对性能的影响极低（由于采用了level1级别的压缩），最高可减少75%的网络IO。

## 服务发现
Agileutil既支持客户端与服务端直连，也支持服务注册发现
（客户端与服务端直连的例子，请参考上面的TcpRpcServer部分）。
目前仅支持基于Consul的服务发现，未来计划支持etcd。TCP/UDP/HTTP这些协议的服务端、客户端类库均支持服务注册发现，下面的例子以TCP为例。


### 健康检查
基于Consul的Check机制。服务注册后，自动添加一个定期的健康检查（默认为TCP端口检查，未来有计划支持HTTP健康检查）。一旦服务进程挂掉，那么客户端将请求到其他健康的服务节点上。同时客户端也存在重试机制，由于健康检查存在时间间隔，可能服务端进程挂掉后，仍需等待一段时间才被Consul发现，这时客户端如果请求到挂掉的服务节点上失败后，客户端会尝试请求其他服务节点进行重试。

### 负载均衡策略
当多个服务端节点，都在注册中心注册后（当前为consul），那么客户端请求需要进行负载均衡。默认使用轮询的负载均衡策略，并支持重试机制。按照轮询策略请求当前的服务端节点时，如果失败，那么会自动重试，尝试请求下一个，直到重试次数满三次为止（除非某个或多个服务端节点出现异常时，才会触发自动重试机制）。

### 快速开始
服务注册发现的使用也很简单，请耐心看完。
- 第一步，你需要定义一个DiscoverConfig对象。
指定用于服务注册发现的Consul的地址和端口。同时通过serviceName参数指定一个全局唯一的服务名称（用于标记服务端服务）。同时指定服务端监听的地址和端口。

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
> 说明:
1.consulHost 和 consulPort 参数指定Consul的地址和端口
2.ServiceName 参数用于标记服务端名称，并通过服务名称进行服务发现，需要保证全局唯一
3.serviceHost和servicePort参数指定服务端监听的端口和地址

- 第二步、调用setDiscoverConfig()方法将DiscoveryConfig对象传入
- 第三步，之后调用serve()方法，开始处理请求
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
### 完整的服务端示例 (UDP/HTTP调用方式相同)
```python
from agileutil.rpc.server import TcpRpcServer
from agileutil.rpc.discovery import DiscoveryConfig

def sayHello(name): 
    return 'hello ' + name

disconf = DiscoveryConfig(
    consulHost = '192.168.19.103',
    consulPort = 8500,
    serviceName = 'test-rpc-server',
    serviceHost = local_ip(),
    servicePort = 10001
)
server = TcpRpcServer('0.0.0.0', 10001)
server.setDiscoverConfig(disconf)
server.regist(sayHello)
server.serve()
```

### 完整的客户端示例（UDP/HTTP调用方式相同）
- 创建DiscoveryConfig对象，指定Consul的地址端口（serviceName参数和服务端的保持一致，且全局唯一）
- 调用setDiscoveryConfig()方法传入服务发现配置
```python
from agileutil.rpc.client import TcpRpcClient
from agileutil.rpc.discovery import DiscoveryConfig
cli = TcpRpcClient()
disconf = DiscoveryConfig(
    consulHost= '192.168.19.103',
    consulPort= 8500,
    serviceName='test-rpc-server'
)
cli.setDiscoveryConfig(disconf)
for i in range(3):
    resp = cli.call(func = 'sayHello', args=('mary', ))
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
PooolDB实现了数据库连接池，并且ORM功能是基于PoolDB实现的。对于常用的数据库操作，如果不使用ORM，直接使用PoolDB也是可以的。

### 定义 PoolDB 对象.
```python
from agileutil.db4 import PoolDB
db = PoolDB(host='127.0.0.1', port=3306, user='root', passwd='', dbName='test2', min_conn_num=10)
db.connect()
```
### 查询记录
```python
sql = 'select * from nation'
rows = db.query(sql)
print(rows)
```
### 删除、修改、插入记录
```python
sql = "insert into nation(name) values('test')"
effect, lastid = db.update(sql)
print(effect,lastid)

sql = "delete from nation where name='test'"
effect, _ = db.update(sql)
print(effect,lastid)
```

## DB
DB 是一个操作数据库的类，和PoolDB的区别是，它不支持数据库连接池，因此更建议使用PoolDB.它的用法和PoolDB是相似的。
### 定义DB对象
```python
from agileutil.db import DB
db = DB(host='127.0.0.1', port=3306, user='root', passwd='', dbName='test2')
```
### 查询记录
```python
sql = 'select * from nation'
rows = db.query(sql)
print(rows)
```
### 修改、删除、插入记录
```python
sql = "insert into nation(name) values('test')"
effetc = db.update(sql)
print(effetc, db.lastrowid())
```

## 日志
Agileutil提供了一个线程安全的Log对象，使用起来非常简单。
```python
from agileutil.log import Log

logger = Log('./debug.log')
logger.info(123, '456')
logger.warning('warning')
logger.error('error')
```

### 日志切割
默认日志按天分割，保留最近7天的，你也可以指定日志保留的天数。
```
logger = Log('./debug.log', logSaveDays=7)
logger.info('info')
```
当然，也可以强制不切割日志，通过isRotate参数。
```
logger = Log('./debug.log', isRotate=False)
logger.info('info')
```

### ERROR级别日志
默认的，ERROR级别的日志，在日志文件中会被标红表示，更加醒目，便于排查问题。
```
logger.error('runtimee exception raise')
```


## 致谢
[![Stargazers repo roster for @lycclsltt/agileutil](https://reporoster.com/stars/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/stargazers)

[![Forkers repo roster for @lycclsltt/agileutil](https://reporoster.com/forks/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/network/members)