'''
example:

from sunyata.redislock import get_redis_lock
import time

rlock = get_redis_lock('192.168.1.1', 6379, 'abcd1234')

while 1:
    if rlock.acquireLock():
        print('accquire lock succed')
        time.sleep(25)
        print('oper finish')
        rlock.releaseLock()
        print('release lock')
        time.sleep(2)
    else:
        time.sleep(2)
        print('wait lock')
'''

import redis
import uuid

class RedisLock(object):
    
    def __init__(self, redisConn, expire=30):
        super().__init__()
        self.redisConn = redisConn
        self.key = 'redis_lock_key'
        self.expire = expire
        self.lastvalue = str(uuid.uuid1())

    def acquireLock(self):
        ret = self.redisConn.setnx(self.key, self.lastvalue)
        if ret:
            self.redisConn.expire(self.key, self.expire)
            return True
        return False

    def releaseLock(self):
        value = self.redisConn.get(self.key)
        if value == None:
            return False
        if value != self.lastvalue:
            return False
        self.redisConn.delete(self.key)
        return True

def get_redis_lock(host,port,password):
    pool = redis.ConnectionPool(host=host, port=port, decode_responses=True, password=password)
    rconn = redis.Redis(connection_pool=pool)
    rlock = RedisLock(rconn)
    return rlock