#coding=utf-8
'''
该模块目前只支持Python2.7

例子：

#coding=utf-8
from agileutil.remote_manage import Server, ServerList

serverList = ServerList (
	Server(ip='192.168.1.1', sshPort=22, sshUser='xxx', sshPwd='xxx'),
	Server(ip='192.168.1.2', sshPort=22, sshUser='xxx', sshPwd='xxx')
)

cmdList = [
	'df -lh',
	'ps -ef'
]

serverList.execCmdList(cmdList)

'''

import paramiko


class Server:
    def __init__(self, ip='', sshPort=22, sshUser='', sshPwd='', timeout=10):
        self.ip = ip
        self.sshPort = sshPort
        self.sshUser = sshUser
        self.sshPwd = sshPwd
        self.timeout = timeout

    def execCmdList(self, cmdList=[]):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print('-----------------------------------')
        try:
            client.connect(hostname=self.ip,
                           port=self.sshPort,
                           username=self.sshUser,
                           password=self.sshPwd,
                           timeout=self.timeout)
            print('connect %s:%s succed' % (self.ip, self.sshPort))
        except Exception as ex:
            print('connect %s:%s failed:%s' % (self.ip, self.sshPort, str(ex)))
            return
        
        ssh = client.invoke_shell()
        if self.sshUser != 'root':
            ssh.send('sudo -s \n')
            buff = ''
            while not buff.endswith('[sudo] password for %s: ' % self.sshUser):
                resp = ssh.recv(9999)
                buff = buff + resp.decode('utf-8')
            ssh.send(self.sshPwd)
            ssh.send('\n')
            buff = ''
            while not buff.endswith('# '):
                resp = ssh.recv(9999)
                buff = buff + resp

            currentUser = 'root'
        else:
            currentUser = self.sshUser

        for cmd in cmdList:
            print('cmd:', cmd)
            ssh.send(cmd + '\n')
            buff = ''
            while not buff.endswith("\r\n"):
                resp = ssh.recv(1)
                buff = buff + resp
            buff = ''
            while not buff.endswith('# '):
                resp = ssh.recv(1)
                buff = buff + resp
            output = buff.split('%s@' % currentUser)[0]
            if output.endswith('\r\n'):
                output = output.strip('\r\n')
            print('output:', output)

        client.close()


class ServerList:
    def __init__(self):
        self.sList = []

    def append(self, serverItem):
        self.sList.append(serverItem)

    def execCmdList(self, cmdList=[]):
        for s in self.sList:
            s.execCmdList(cmdList)
