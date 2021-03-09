#coding=utf-8
'''
pip install pexpect
'''

import pexpect


class SSHClient(object):

    __slots__ = ['_host', '_port', '_user', '_pwd', '_ssh']

    def __init__(self, host, port, user, pwd):
        self._host = host
        self._port = port
        self._user = user
        self._pwd = pwd
        self._ssh = None

    def run(self, cmd):
        ssh_newkey = 'Are you sure you want to continue connecting'
        child = pexpect.spawn('ssh -l %s -p %s %s %s' %
                              (self._user, self._port, self._host, cmd))
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
        if i == 0:  #timeout
            raise Exception('ssh timeout')
        if i == 1:  #SSH does not have the public key. Just accept it.
            child.sendline('yes')
            child.expect('password: ')
            i = child.expect([pexpect.TIMEOUT, 'password: '])
            if i == 0:  #timeout
                raise Exception('ssh timeout')
        child.sendline(self._pwd)
        child.expect(pexpect.EOF)
        return child.before

    def getAddr(self):
        return self._host + ':' + str(self._port)


def ssh_exec(host, port, user, pwd, cmd):
    client = SSHClient(host, port, user, pwd)
    return client.run(cmd)


def batch_ssh_exec(host_list, user, pwd, cmd, port=22):
    for host in host_list:
        print(ssh_exec(host, port, user, pwd, cmd))
