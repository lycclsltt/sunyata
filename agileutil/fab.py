#codiing=utf-8
'''
pip install fabric
'''

from fabric.api import *
from fabric.context_managers import *
import sys


def batchSetHosts(serverList, hostList, delHostList=[]):
    """
	This function will set /etc/hosts.If the host
	has been exist in hosts file, then it will be
	overwrite, else it will be append to the hosts
	file.

	:param serverList list: a list of {'host':'xxx', 'port':'xx', 'user':'xx', 'password':''xx}
	:param hostList list: a list of {'ip domain1 domain2'}
	:param delHostList list: a list of domain
	"""
    def sortedByKeys(dic):
        keys = dic.keys()
        keys.sort()
        retDic = {}
        for key in keys:
            retDic[key] = dic[key]
        return retDic

    for server in serverList:
        env.host_string = server['host']
        env.port = server['port']
        env.user = server['user']
        env.password = server['password']
        ret = sudo('cat /etc/hosts')
        lines = ret.split('\n')
        hostHash = {}
        newHostList = []
        for line in lines:
            line = line.replace('\n', '')
            line = line.replace('\r', '')
            line = line.strip()
            if line == '':
                continue
            if line.replace(' ', '') == '':
                continue
            if line[0] == '#':
                newHostList.append(line)
                continue
            items = line.split(' ')
            ip = items[0].strip()
            for i in xrange(len(items)):
                if i == 0:
                    continue
                domain = items[i]
                domain = domain.strip()
                if domain == '':
                    continue
                if domain in delHostList:
                    continue
                hostHash[domain] = ip
        setHostHash = {}
        for host in hostList:
            host = host.strip()
            items = host.split(' ')
            ip = items[0].strip()
            for i in xrange(len(items)):
                if i == 0:
                    continue
                domain = items[i]
                domain = domain.strip()
                if domain == '':
                    continue
                if domain in delHostList:
                    continue
                setHostHash[domain] = ip
        for domain, ip in setHostHash.items():
            hostHash[domain] = ip
        hostHash = sortedByKeys(hostHash)
        for domain, ip in hostHash.items():
            hostline = ip + ' ' + domain
            newHostList.append(hostline)
        newHostList.sort()
        hosts = '\n'.join(newHostList)
        sudo("echo '%s' > /etc/hosts" % (hosts))


def exeCmd(cmd):
    return sudo(cmd)


def batchLoopExec(serverList, cmdList):
    """
	This function will exec cmd on the server in
	hostList one by one. The commond will be execute on
	next server when the last server has ran the command.
	"""

    for server in serverList:
        #env.hosts = [ server['host'] ]
        env.host_string = server['host']
        env.port = server['port']
        env.user = server['user']
        env.password = server['password']
        for cmd in cmdList:
            exeCmd(cmd)


def batchSyncExec(serverList, cmdList):
    """
	This function will exec cmd on the server with cmd
	step by step instead of by server on by on.So the same
	command will execute on all server, then the next command
	will be execute.
	"""
    for cmd in cmdList:
        for server in serverList:
            env.host_string = server['host']
            env.port = server['port']
            env.user = server['user']
            env.password = server['password']
            exeCmd(cmd)
