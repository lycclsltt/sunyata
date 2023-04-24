from sunyata.rpc.server import TcpRpcServer, rpc

@rpc
def hello(name):
    return 'hello ' + name

app = TcpRpcServer('0.0.0.0', 9998)
app.serve()