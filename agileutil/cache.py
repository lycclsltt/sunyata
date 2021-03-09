#coding=utf-8
'''
base on bsddb, key and value must be string or buffer
suport set, get, delete, has_key, setex, keys, values, flushall
'''

import time
try:
    import bsddb3 as bsddb
except:
    import bsddb


class Cache:
    def __init__(self, db_file):
        self._db_file = db_file
        self._db = bsddb.btopen(self._db_file, 'c')

    def set(self, k, v):
        k, v = str(k), str(v)
        self._db[k] = v
        return self

    def get(self, k, default_v=None):
        k = str(k)
        time_set_k = self._gen_time_set_key(k)
        time_expire_k = self._gen_time_expire_key(k)
        v = None
        time_set_v = None
        time_expire_v = None
        try:
            v = self._db[k]
        except:
            pass
        try:
            time_set_v = self._db[time_set_k]
        except:
            pass
        try:
            time_expire_v = self._db[time_expire_k]
        except:
            pass
        if time_set_v and time_expire_v:
            '''
			add by setex()
			'''
            set_time = float(time_set_v)
            expire_time = float(time_expire_v)
            if time.time() - set_time >= expire_time:
                self._db.pop(k)
                self._db.pop(time_set_k)
                self._db.pop(time_expire_k)
                return default_v
        if v == None:
            return default_v
        return v

    def has_key(self, k):
        if self.get(k):
            return True
        else:
            return False

    def delete(self, k):
        k = str(k)
        self._db.delete(k)
        return self

    def setex(self, k, v, seconds):
        k, v, seconds = str(k), str(v), int(seconds)
        time_set_k = self._gen_time_set_key(k)
        time_expire_k = self._gen_time_expire_key(k)
        cur_time = str(time.time())
        if seconds == 0: return
        if seconds < 0:
            self.set(k, v)
            return
        self.set(k, v)
        self.set(time_set_k, cur_time)
        self.set(time_expire_k, seconds)
        return self

    def _gen_time_set_key(self, k):
        return 'agileutil_cache_time_set_k_%s' % k

    def _gen_time_expire_key(self, k):
        return 'agileutil_cache_time_expire_k_%s' % k

    def keys(self):
        return filter(
            lambda x: 'agileutil_cache_time_set_k' not in x and
            'agileutil_cache_time_expire_k_' not in x, self._db.keys())

    def values(self):
        return filter(lambda x: x is not None,
                      [self.get(k) for k in self.keys()])

    def flushall(self):
        self._db.clear()
        return self

    def delete(self, k):
        k = str(k)
        return self._db.pop(k)
