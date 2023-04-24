from sunyata.http.server import HttpServer, route
from sunyata.rpc.client import HttpRpcClient

@route('/query', methods=['GET'])
def query(request):
    domain = request.data.get('domain')
    cli = HttpRpcClient('127.0.0.1', 9988)
    ip = cli.DnsService.query(domain)
    return ip

app = HttpServer()
app.serve()