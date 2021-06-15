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

c = TcpRpcClient('127.0.0.1', 9988, timeout=5)
resp = c.call(func = 'sayHello', args = ('zhangsan'))
print('resp', resp)
```

### HTTP RPC Server
Agileutil also provides Remote Procedure Call (RPC) based on HTTP protocol, with the underlying implementation based on HTTP protocol and built-in web framework.It is very simple to use and is very similar to TcpRpcServer.
```python
from agileutil.rpc.server import HttpRpcServer

def sayHello(name):
    return 'hello ' + name

s = HttpRpcServer('0.0.0.0', 9988, workers=1)
s.regist(sayHello)
s.serve()
```

### HTTP RPC Client
Again, the client needs to use the corresponding HttpRcpClient.
```python
from agileutil.rpc.client import HttpRpcClient

cli = HttpRpcClient('127.0.0.1', 9988)
for i in range(10):
    resp = cli.call(func = 'sayHello', args=('zhangsan'))
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
Currently only Consul based service registration and discovery is supported.Future plans support ETCD.Both the server and the client libraries of the TCP/HTTP/UDP protocol support service registration and discovery. The following example takes TCP as an example.

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

### Complete client-side example 
Initialize a DiscoveryTcpRpcClient object from the DiscoveryConfig object
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
    resp = cli.call(func = 'sayHello', args=('mary'))
```

[![Stargazers repo roster for @lycclsltt/agileutil](https://reporoster.com/stars/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/stargazers)

[![Forkers repo roster for @lycclsltt/agileutil](https://reporoster.com/forks/lycclsltt/agileutil)](https://github.com/lycclsltt/agileutil/network/members)