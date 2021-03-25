#coding=utf-8
'''
常用的装饰器
'''
from multiprocessing import Process
import functools
import time
import agileutil.date as dt
import socket


def stdout_log(func):
    '''
    打印方法耗时到标准输出
    例如: [2020-06-23 10:19:09] call test() method, args:(1, 2), return:3, cost:2.113 seconds
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        begin = time.time()
        ret = func(*args, **kwargs)
        cost = time.time() - begin
        #print('[%s] call %s() method, args:%s, return:%s, cost:%s seconds' %
        #      (dt.current_time(), func.__name__, str(args), str(ret),
        #       round(cost, 3)))
        return ret

    return wrapper


EXCEPTION = 'agileutil_wrap_exception'


def safe(func):
    '''
    对方法进行异常处理，异常不会被抛出, 减少导致进程crash的情况
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = EXCEPTION
        try:
            ret = func(*args, **kwargs)
        except Exception as ex:
            pass
            #print(
            #    '[%s] catch exception when call %s() method, args:%s, ex:%s' %
            #    (dt.current_time(), func.__name__, str(args), str(ex)))
        return ret

    return wrapper


def retryTimes(retryTimes=2):
    '''
    如果装饰的方法抛出异常，那么进行重试n次，默认重试1次
    如果重试n次后仍然异常，那么抛出最后一个异常
    '''
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
                    #print(
                    #    '[%s] catch exception when call %s() method, args:%s, ex:%s, ready retry'
                    #    %
                    #    (dt.current_time(), func.__name__, str(args), str(ex)))
            raise lastEx

        return wrapper

    return function


def retry(func):
    '''
    如果装饰的方法抛出异常，那么进行重试1次
    如果重试1次后仍然异常，那么抛出最后一个异常
    '''
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
                #print(
                #    '[%s] catch exception when call %s() method, args:%s, ex:%s, ready retry'
                #    % (dt.current_time(), func.__name__, str(args), str(ex)))
        raise lastEx

    return wrapper


def loop(func):
    '''
    当方法返回后，重新执行该方法
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while 1:
            func(*args, **kwargs)

    return wrapper


def subprocess(func):
    '''
    在子进程中并发的执行此方法
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        p = Process(target=func, args=args, kwargs=kwargs)
        p.start()

    return wrapper


FUNC_EXEC_MAP = {}


def exec_once(func):
    '''
    被装饰的方法只会执行一次，之后即使显示调用，也不会被执行
    '''
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
    '''
    被装饰的方法只会执行一次，之后即使显示调用，也不会被执行
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        return str(ret)

    return wrapper
