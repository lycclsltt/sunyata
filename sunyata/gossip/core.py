from sunyata.rpc.server import HttpRpcServer
from sunyata.rpc.client import HttpRpcClient
from sunyata.rpc import rpc
import queue
import threading
import time


@rpc
class GossipSyncedCallback(object):
    
    syncedCallbackClassInstance = None
    
    def synced(self, msg):
        if self.syncedCallbackClassInstance:
            self.syncedCallbackClassInstance.synced(msg)
        else:
            print('synced recv', msg.k, msg.v, msg.version)
            

class GossipMsg(object):
    
    def __init__(self, k, v, version):
        self.k = k
        self.v = v
        self.version = version


class GossipCore(object):
    
    def __init__(self, bindHost, bindPort, memberAddrs, syncedCallback=None):
        self.memberAddrs = memberAddrs
        self.bindHost = bindHost
        self.bindPort = bindPort
        self.rpcServer = HttpRpcServer(self.bindHost, self.bindPort)
        self.rpcServer.accessLog = False
        self.rpcServer.app.accessLog = False
        self.rpcClientList = [ HttpRpcClient(memberAddr['host'], memberAddr['port']) for memberAddr in self.memberAddrs ]
        if syncedCallback:
            GossipSyncedCallback.syncedCallbackClassInstance = syncedCallback
        self.queueMaxSize = 100000
        self.Q = queue.Queue(self.queueMaxSize)
        self.thlist = []
        
    def startRpcServer(self):
        self.rpcServer.serve()
        
    def startBroadcast(self):
        while 1:
            msg = self.Q.get()
            for cli in self.rpcClientList:
                #if cli.host == self.bindHost and cli.port == self.bindPort:
                #    continue
                try:
                    cli.GossipSyncedCallback.synced(msg)
                except Exception as ex:
                    print(ex)
        
    def start(self):
        thRpcServer = threading.Thread(target=self.startRpcServer)
        thRpcServer.start()
        self.thlist.append(thRpcServer)
         
        thBroadcast = threading.Thread(target=self.startBroadcast)
        thBroadcast.start()
        self.thlist.append(thBroadcast)
            
    def broadcast(self, msg):
        self.Q.put(msg)
        
    def join(self):
        for th in self.thlist:
            th.join()