#coding=utf-8

from multiprocessing import Process
from kazoo.client import KazooClient
import platform
import time


def log_info(logger, string):
    if logger: logger.info('[zk] ' + string)


def log_warn(logger, string):
    if logger: logger.warning('[zk] ' + string)


def log_error(logger, string):
    if logger: logger.error('[zk] ' + string)


zk = None


def register(zknodes, path, child_node_name, child_node_value, logger):
    if platform.python_version()[0] != '2':
        child_node_value = child_node_value.encode('utf-8')
    global zk
    if zk == None:
        zk = KazooClient(hosts=zknodes)
        zk.start()
    if not zk.exists(path):
        log_warn(logger, "%s not exist" % path)
        zk.ensure_path(path)
        log_info(logger, "create %s" % path)
    if path[-1] != '/': path = path + '/'
    k = path + child_node_name
    if not zk.exists(k):
        log_warn(logger, "%s not exist" % k)
        zk.create(k, child_node_value, ephemeral=True)
        log_info(logger, "create %s" % k)
    else:
        zk.set(k, child_node_value)
    children = zk.get_children(path)
    log_info(logger, "get current childrent:" + str(children))


def loop_register(zknodes,
                  path,
                  child_node_name,
                  child_node_value,
                  intval=30,
                  logger=None,
                  is_regist_callback=None):
    while True:
        try:
            is_regist = True
            if is_regist_callback:
                is_regist = is_regist_callback(child_node_name,
                                               child_node_value)
            if is_regist:
                register(zknodes, path, child_node_name, child_node_value,
                         logger)
                log_info(logger, "regist succed")
            else:
                global zk
                if zk:
                    zk.stop()
                    zk.close()
                    zk = None
                log_error(logger,
                          "is_regist_callback check failed, not regist")
        except Exception as ex:
            log_error(logger, "regist failed:" + str(ex))
        time.sleep(intval)


def start_loop_register(zknodes,
                        path,
                        child_node_name='',
                        child_node_value='',
                        intval=30,
                        logger=None,
                        is_regist_callback=None):
    p = Process(target=loop_register,
                args=(zknodes, path, child_node_name, child_node_value, intval,
                      logger, is_regist_callback))
    p.start()
    return


def get_children(zknodes, path):
    zkcli = KazooClient(hosts=zknodes)
    zkcli.start()
    if path[-1] != '/': path = path + '/'
    children = zkcli.get_children(path)
    m = {}
    for child in children:
        m[child] = zkcli.get(path + child)[0]
    zkcli.stop()
    zkcli.close()
    return m


'''
def is_regist(node_name, node_val):
    return True

num = 1
def test(node_name, node_val):
    global num
    num = num + 1
    if num > 30:
        return True
    if num > 10:
        return False
    return True

from log import Log
log = Log("./debug.log")
log.setOutput(True)
start_loop_register('127.0.0.1:2181', '/test/1', 'a', 'a', 3, log, is_regist_callback=is_regist)
start_loop_register('127.0.0.1:2181', '/test/1', 'b', 'b', 3, log, is_regist_callback=test)
'''
