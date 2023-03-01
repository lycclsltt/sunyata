import functools
import redis
import pickle

FUNC_CACHE_MAP = {}

def _get_key(funcname, *args, **kwargs):
    key = 'sunyata_cache_func:'+funcname + ':'
    if len(args) > 0:
        key = key + str(list(args)) + ':'
    if len(kwargs) > 0:
        key = key + str(dict(kwargs))
    return key

def cache_func(*args, **kwargs):
    def function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global FUNC_CACHE_MAP
            key = _get_key(func.__name__, *args, **kwargs)
            if key in FUNC_CACHE_MAP:
                return FUNC_CACHE_MAP[key]
            ret = func(*args, **kwargs)
            FUNC_CACHE_MAP[key] = ret
            return ret
        return wrapper
    return function

def get_redis_connection(connstr):
    host, port, db = connstr.split(':')
    conn = redis.Redis(host=host,port=port,db=db)
    return conn

def redis_cache_func(connstr='127.0.0.1:6379:1', expireSeconds=3600*24):
    conn = get_redis_connection(connstr)
    def function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _get_key(func.__name__, *args, **kwargs)
            val = conn.get(key)
            if val != None:
                return pickle.loads(val)
            ret = func(*args, **kwargs)
            val = pickle.dumps(ret)
            conn.set(key, val)
            conn.expire(key, expireSeconds)
            return ret
        return wrapper
    return function