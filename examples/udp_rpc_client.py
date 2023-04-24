from sunyata.rpc.client import UdpRpcClient

cli = UdpRpcClient('127.0.0.1', 9998)
res = cli.hello('world')
print(res)