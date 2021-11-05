## 特性
- 像本地函数一样调用
- 使用简单，用户只需要关注业务即可
- HTTP/UDP/TCP 全协议支持
- 支持异步 async/await
- 支持服务注册、发现

## 快速开始
myservice.py
```python
from agileutil.rpc.server import rpc

@rpc
def add(n1, n2):
    return n1 + n2
```
启动：
```shell
agileutil --run myservice
```
![pic2.png](./docs/pic2.png)


请求
```
from agileutil.rpc.client import TcpRpcClient

cli = TcpRpcClient('127.0.0.1', 9988, timeout=100000)
res = cli.add(1, 2
print(res)
``` 

[文档](./DETAIL.md)