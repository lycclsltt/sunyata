from sunyata.rpc.server import UdpRpcServer, rpc

@rpc
def hello(name):
    return 'hello ' + name

app = UdpRpcServer('0.0.0.0', 9998)
app.serve()