#### 目录
- [简介](#简介)
- [快速开始](#快速开始)
  - [Python 版本要求](#python-版本要求)
  - [安装](#安装)
  - [TCP RPC 服务端](#tcp-rpc-服务端)
  - [TCP RPC 客户端](#tcp-rpc-客户端)
  - [指定多个服务端地址](#指定多个服务端地址)
  - [HTTP RPC 服务端](#http-rpc-服务端)
  - [HTTP RPC Client](#http-rpc-client)
  - [UDP RPC 服务端](#udp-rpc-服务端)
  - [UDP RPC 客户端](#udp-rpc-客户端)
- [服务发现](#服务发现)
  - [健康检查](#健康检查)
  - [快速开始](#快速开始-1)
  - [完整的服务端示例 (UDP/HTTP调用方式相同)](#完整的服务端示例-udphttp调用方式相同)
  - [完整的客户端示例（UDP/HTTP调用方式相同）](#完整的客户端示例udphttp调用方式相同)
- [数据压缩](#数据压缩)
## 简介

Agileutil是一个Python3 RPC框架。基于微服务架构，封装了rpc/http/orm/log等常用组件，提供了简洁的API，开发者可以很快上手，快速进行业务开发。

## 快速开始

### Python 版本要求
Python >= 3.6


### 安装
```
pip install agileutil
```

### TCP RPC 服务端
下面是一个TCP协议的服务端例子。
- 创建一个TcpRpcServer对象, 指定服务端监听地址和端口
- 通过@rpc装饰器注册需要被客户端请求的方法
- 调用serve()方法，开始处理客户端请求
```python
from agileutil.rpc.server import TcpRpcServer, rpc

@rpc
class TestService:

    def hello(self, name):
        return "Hello, {}!".format(name)

    def add(self, a, b, c):
        return a + b + c

@rpc
def hello(name):
    return "Hello, {}!".format(name)

server = TcpRpcServer('0.0.0.0', 9988)
server.serve()
```

### TCP RPC 客户端
- 创建TcpRpcClient对象，指定RPC服务端地址
- 通过call()方法，指定服务端方法名称和参数（注意：如果方法名不存在，或者服务端未调用@rpc装饰器注册，那么call()方法将抛出异常）
- call() 方法的返回值和在本地调用一样，原来是什么返回类型，就还是什么（例如返回字典、列表、对象甚至内置类型，经过序列化后，不会发生改变）
```python
from agileutil.rpc.client import TcpRpcClient

cli = TcpRpcClient('127.0.0.1', 9988, timeout = 2)
resp = cli.call('TestService.hello', args=('xiaoming',))
print(resp)
resp = cli.call('TestService.add', args=(1, 2, 3))
print(resp)
resp = cli.call('hello', args=('xiaoming',))
print(resp)
```

### 指定多个服务端地址
- 通过servers参数，你可以创建一个指定多个服务端地址的client对象，默认采用轮询的负载均衡策略，将请求转发到多个server上，如果请求其中一个server出现了失败，那么会自动重试。
```python
from agileutil.rpc.client import TcpRpcClient

c = TcpRpcClient(servers = ['127.0.0.1:9988', '127.0.0.1:9989'])
resp = c.call(func = 'hello', args = 'zhangsan')
print(resp)
```

### HTTP RPC 服务端
底层是基于高性能的Sanic异步web框架实现的，使用起来非常简单，和TcpRpcServer的用法类似:
```python
from agileutil.rpc.server import HttpRpcServer, rpc

@rpc
def sayHello(name):
    return 'hello ' + name

s = HttpRpcServer('0.0.0.0', 9988, workers=1)
s.serve()
```

### HTTP RPC Client
客户端使用对应的HttpRpcClient对象:
```python
from agileutil.rpc.client import HttpRpcClient

c = HttpRpcClient('127.0.0.1', 9988)
for i in range(10):
    resp = c.call(func = 'sayHello', args=('zhangsan', ))
    print(resp)
```

### UDP RPC 服务端
将TcpRpcServer替换为UdpRpcServer即可。
- 创建UdpRpcServer对象，指定监听的地址和端口
- 调用regist()方法，将需要被客户端请求的方法注册进去
- 调用serve()方法开始处理客户端请求
- 返回的内容和调用本地方法没有差别，框架内部通过序列化和反序列化，将数据转化为程序内的对象（字典、列表、内置类型、各种类对象等等）
```python
from agileutil.rpc.server import UdpRpcServer, rpc

@rpc
def sayHello(name): 
    return 'hello ' + name

server = UdpRpcServer('0.0.0.0', 9988)
server.serve()
```
### UDP RPC 客户端
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

## 服务发现
除了客户端与服务端直连，也支持服务注册发现（客户端与服务端直连的例子，请参考上面的TcpRpcServer部分）。
目前仅支持基于Consul的服务发现，未来计划支持etcd。下面的例子以TCP为例。


### 健康检查
基于Consul的Check机制，服务注册后，自动添加一个定期的检查任务。默认为TCP端口检查，支持TCP/HTTP RPC服务端，UDP服务端暂不支持。一旦服务进程挂掉，那么客户端会请求到其他健康的服务端节点上。

### 快速开始
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
> 1.consulHost 和 consulPort 参数指定Consul的地址和端口 
> 2.ServiceName 参数用于标记服务端名称，并通过服务名称进行服务发现，需要保证全局唯一 
> 3.serviceHost和servicePort参数指定服务端监听的端口和地址

- 第二步、调用setDiscoverConfig()方法将DiscoveryConfig对象传入
- 第三步，调用serve()方法，开始处理请求
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
from agileutil.rpc.server import TcpRpcServer, rpc
from agileutil.rpc.discovery import DiscoveryConfig

@rpc
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
resp = cli.call(func = 'sayHello', args=('mary', ))
print(resp)
```

## 数据压缩
默认采用lz4进行压缩、解压缩（经过测试，它的压缩效果和gzip, zlib比较接近，压缩、解压缩性能是zlib的10倍左右）。
在数据传输大于4KB时，自动开启进行压缩。对端根据一个标记位进行判断，自动进行解压缩处理（或不处理，未经过压缩的情况）。开发者无需关心
数据的压缩、解压缩过程，经过测试对性能的影响极低（由于采用了level1级别的压缩），最高可减少75%的网络IO。


[![Stargazers repo roster for @lycclsltt/agileutil](https://reporoster.com/stars/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/stargazers)

[![Forkers repo roster for @lycclsltt/agileutil](https://reporoster.com/forks/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/network/members)