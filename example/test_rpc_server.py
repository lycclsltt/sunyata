#coding=utf-8

from agileutil.rpc.server import TcpRpcServer
from agileutil.db4 import PoolDB

db = PoolDB('127.0.0.1', 3306, 'root', '', 'test2')
db.connect()

def sayHello(name):
    sql = 'select * from nation limit 100000'
    rows = db.query(sql)
    return 'hello ' + name

nationServer = TcpRpcServer('0.0.0.0', 9988)
nationServer.regist(sayHello)
nationServer.serve()