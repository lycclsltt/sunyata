#coding=utf-8

import mail


def send(content='', title='agileutil_alarm', mail_to='lycclsltt@163.com'):
    try:
        mail.send(from_addr='agileutil_alarm@agileutil.com',
                  to_addr=mail_to,
                  title=title,
                  content=content)
    except:
        pass
