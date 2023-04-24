from sunyata.rpc.server import HttpRpcServer, rpc

@rpc
def hello(name):
    return 'hello ' + name

app = HttpRpcServer('0.0.0.0', 9998)
app.serve()