import os
import socket
import commands
import time
import sys

RECIEVER = 'xxx@xxxx.cn'


def sendmail(sender, reciever, title, content):
    cmd = "echo '%s' | mail -s '%s' -r '%s' '%s'" % (content, title, sender,
                                                     reciever)
    commands.getstatusoutput(cmd)


def notify(user, action):
    if user.strip() == '': return
    hostname = socket.gethostname()
    curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    sendmail(
        'ssh_notify@' + hostname,
        RECIEVER,
        'user %s %s %s at %s' % (user, action, hostname, curTime),
        'user %s %s %s at %s' % (user, action, hostname, curTime),
    )


pid = os.fork()
if pid != 0: sys.exit(0)

users = []
firstTag = True

while True:
    status, output = commands.getstatusoutput('users')
    curUsers = list(set(output.split(' ')))
    if 'root' in curUsers: curUsers.remove('root')
    for user in curUsers:
        if user not in users:
            users.append(user)
            if not firstTag: notify(user, 'login')
    for user in users:
        if user not in curUsers:
            users.remove(user)
            notify(user, 'logout')
    firstTag = False
    time.sleep(5)
