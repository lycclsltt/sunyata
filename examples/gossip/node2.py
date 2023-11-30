from sunyata.gossip.core import GossipCore, GossipSyncedCallback, GossipMsg
import time

class MyCallback(GossipSyncedCallback):
    
    def __init__(self):
        self.m = {}
    
    def synced(self, msg):
        self.m[msg.k] = msg

callbackClass = MyCallback()
gc = GossipCore(bindHost='127.0.0.1', bindPort=8083, memberAddrs=[{'host':'127.0.0.1', 'port':8083}, {'host':'127.0.0.1', 'port':8082}, {'host':'127.0.0.1', 'port':8081}], syncedCallback=callbackClass)
gc.start()

time.sleep(3)

for i in range(3):
    time.sleep(1)
    gc.broadcast(GossipMsg('node2_' + str(i), str(i), 0))
    
time.sleep(5)
s = ""
for k, msg in callbackClass.m.items():
    s = s + msg.k + '-' + msg.v

print(s)
    
    