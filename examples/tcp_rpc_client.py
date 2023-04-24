from sunyata.rpc.client import TcpRpcClient

cli = TcpRpcClient('127.0.0.1', 9998)
res = cli.hello('world')
print(res)