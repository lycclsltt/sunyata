from multiprocessing import Process
import functools
import time
import socket
from dataclasses import dataclass


def stdout_log(func):
    '''
    print to stdout
    for example: [2020-06-23 10:19:09] call test() method, args:(1, 2), return:3, cost:2.113 seconds
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        begin = time.time()
        ret = func(*args, **kwargs)
        cost = time.time() - begin
        return ret

    return wrapper


EXCEPTION = 'sunyata_wrap_exception'


def safe(func):
    '''
    catch exception
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = EXCEPTION
        try:
            ret = func(*args, **kwargs)
        except Exception as ex:
            pass
        return ret

    return wrapper


def retryTimes(retryTimes=2):
    if retryTimes <= 0:
        retryTimes = 1
    
    def function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ret = None
            lastEx = None
            for i in range(retryTimes):
                try:
                    ret = func(*args, **kwargs)
                    return ret
                except socket.timeout as ex:
                    raise ex
                except Exception as ex:
                    lastEx = ex
            raise lastEx

        return wrapper

    return function


def retry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = None
        lastEx = None
        for i in range(2):
            try:
                ret = func(*args, **kwargs)
                return ret
            except socket.timeout as ex:
                raise ex
            except Exception as ex:
                lastEx = ex
        raise lastEx

    return wrapper


def loop(func):
    '''
    loop exec function when it return
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while 1:
            func(*args, **kwargs)

    return wrapper


def subprocess(func):
    '''
    run in sub process
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        p = Process(target=func, args=args, kwargs=kwargs)
        p.start()

    return wrapper


FUNC_EXEC_MAP = {}


def exec_once(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global FUNC_EXEC_MAP
        if func.__name__ in FUNC_EXEC_MAP:
            return
        ret = func(*args, **kwargs)
        FUNC_EXEC_MAP[func.__name__] = 1
        return ret

    return wrapper


def force_return_string(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        return str(ret)

    return wrapper


FUNC_REQUESTNUM_MAP = {}


@dataclass
class RateLimitItem:
    laststamp: int
    count: int


def ratelimit(perSecondMaxRequest):
    if type(perSecondMaxRequest) != int or perSecondMaxRequest < 0:
        raise Exception('ratelimit param perSecondMaxRequest is invalid')
    def function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = int(time.time())
            global FUNC_REQUESTNUM_MAP
            if func.__name__ in FUNC_REQUESTNUM_MAP:
                ritem = FUNC_REQUESTNUM_MAP[func.__name__]
                if now - ritem.laststamp >= 1:
                    ritem.laststamp = now
                    ritem.count = 1
                    FUNC_REQUESTNUM_MAP[func.__name__] = ritem
                else:
                    FUNC_REQUESTNUM_MAP[func.__name__].count += 1
            else:
                FUNC_REQUESTNUM_MAP[func.__name__] = RateLimitItem(laststamp=now, count=1)
            if FUNC_REQUESTNUM_MAP[func.__name__].count > perSecondMaxRequest:
                raise Exception('execced per second max request %s' % perSecondMaxRequest)
            ret = func(*args, **kwargs)
            return ret
        return wrapper

    return function


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner