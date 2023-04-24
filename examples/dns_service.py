from sunyata.rpc.server import HttpRpcServer, rpc

@rpc
class DnsService(object):

    def query(self, domain):
        print('domain', domain)
        return domain + ' A IN 192.168.1.1'

rpcServer = HttpRpcServer(host='0.0.0.0', port=9988)
rpcServer.serve()