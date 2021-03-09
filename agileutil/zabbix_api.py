#coding=utf-8

import requests
import json
import os

class ZabbixAPI:

    def __init__(self, baseurl, username, password):
        self.baseurl = baseurl
        self.username = username
        self.password = password
        self.timeout = 10
        self.headers = {
            'Content-Type': 'application/json-rpc'
        }
        self.token = None
        self.url = self.baseurl + '/zabbix/api_jsonrpc.php'

    def get_token(self):
        '''
        根据username,password获取token
        :return: str
        '''
        if self.token != None:
            return self.token
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.password
            },
            "id": 1,
            "auth": None
        }
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout = self.timeout)
        self.token = r.json()['result']
        return self.token

    def __del__(self):
        self.logout()

    def logout(self):
        '''
        注销登录
        :return: bool
        '''
        if self.token == None:
            return
        data = {
            'jsonrpc': '2.0',
            'method': 'user.logout',
            'params': [],
            'id': 1,
            'auth': self.token
        }
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout = self.timeout)
        if r.json()['result'] == True:
            self.token = None
            print('logout true')
            return True
        else:
            raise Exception('logout fail ' + r.text)

    def get_hostid_info_by_field(self, fileld_name, item_list):
        data = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {
                'output': [
                    'hostid',
                    'host',
                ],
                'filter' : {
                    fileld_name : item_list,
                }
            },
            'auth': self.get_token(),
            'id': 1
        }
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout = self.timeout)
        res = r.json()
        if res.has_key('result'):
            result = res['result']
            if len(result) > 0:
                return result
        raise Exception('host not found' + str(item_list))

    def get_hostid_by_host(self, hostname):
        '''
        根据主机名，获取zabbix中的hostid
        :param hostname: str
        :return: str
        '''
        hostlist = self.get_hostid_info_by_field('host', [ hostname ])
        if len(hostlist)  == 0:
            raise Exception('hostname not found')
        host_dict = hostlist[0]
        if host_dict.get('host', '') == hostname:
            return host_dict.get('hostid')
        raise Exception('hostname not found')

    def get_items_by_host(self, hostname, output = [], fmt = None):
        hostid = self.get_hostid_by_host(hostname)
        data = {
            'jsonrpc': '2.0',
            'method': 'item.get',
            'params': {
                'hostids': hostid,
                'search': {
                    #key: value,
                }
            },
            "id": 1,
            "auth": self.get_token(),
        }
        if len(output) > 0:
            data['params']['output'] = output
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        if fmt == 'json':
            return r.text
        return r.json()['result']

    def get_triggers_by_itemids(self, itemids = [], output = [], fmt=None):
        if len(itemids) == 0:
            return []
        data = {
            'jsonrpc': '2.0',
            'method': 'trigger.get',
            'params': {
                'itemids': itemids,
                'selectFunctions': 'extend'
            },
            "id": 1,
            "auth": self.get_token(),
        }
        if len(output) > 0:
            data['params']['output'] = output
        print('data:', data)
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        if fmt == 'json':
            return r.text
        return r.json()['result']
    
    '''
    def get_host_triggers(self, hostname):
        data = {
            'jsonrpc': '2.0',
            'method': 'trigger.get',
            'params': {
                #'output': [
                #    'triggerid',
                #    'expression',
                #    'description',
                #],
                'filter': {
                    'host': hostname,
                }
            },
            'auth': self.get_token(),
            'id': 1
        }
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        print(r.text, r.status_code)
    '''


    def update_trigger(self, trigger_id, expr):
        data = {
            'jsonrpc': '2.0',
            'method': 'trigger.update',
            'params': {
                "triggerid": trigger_id,
                "expression": expr,
            },
            'auth': self.get_token(),
            'id': 1
        }
        r = requests.post(url=self.url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        print(r.text, r.status_code)


if __name__ == '__main__':
    zapi = ZabbixAPI('http://192.168.21.117', 'xxxx', 'xxxx')
    #获取token
    print( zapi.get_token() )
    #根据主机名获取id
    hostid = zapi.get_hostid_by_host('xxxx-01')
    print('hostid:', hostid)
    #根据某字段获取主机
    hostids_info = zapi.get_hostid_info_by_field('host', ['xxxx-01', '192.168.0.1'])
    print('hostids_info:', hostids_info)
    #获取某主机的所有监控项
    items = zapi.get_items_by_host('xxxx-01', output=['itemid', 'name', 'key_', 'status'])
    #获取服务的监控项
    ser_items = [ elem for elem in items if '_auto_' in elem.get('name') ]
    print('ser_items:', ser_items)
    #获取监控对应的trigger
    itemids = [seri.get('itemid') for seri in ser_items]
    itemids = ['33133']
    print('itemids:', itemids)
    #triggers = zapi.get_triggers_by_itemids(itemids=itemids, output=['triggerid', 'expression', 'description', 'status', 'functions', 'priority'], fmt='json')
    triggers = zapi.get_triggers_by_itemids(itemids=itemids, output=[], fmt='json')
    print('triggers:', triggers)
    expr = """{dddddd:errorlog[/data/logs/dddddd/error.log].count(#1, 30, "lt")}=1"""
    zapi.update_trigger('19037', expr)