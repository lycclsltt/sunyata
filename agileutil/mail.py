#coding=utf-8

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from envelopes import Envelope
from email.header import Header


def send(
    from_addr,
    to_addr,
    host='localhost',
    port=25,
    cc_addr='',
    title='',
    content='',
    html_content='',
):
    if html_content.strip() == '':
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Cc'] = cc_addr
        msg['Subject'] = Header(title, 'utf-8').encode()
        s = smtplib.SMTP(host=host, port=port)
        s.sendmail(from_addr=from_addr, to_addrs=to_addr, msg=msg.as_string())
        return True
    else:
        envelope = Envelope(from_addr=tuple(from_addr.split(',')),
                            to_addr=tuple(to_addr.split(',')),
                            cc_addr=tuple(cc_addr.split(',')),
                            subject=title,
                            html_body=html_content)
        envelope.send(host=host)
        return True


def send_by_pass(from_addr,
                 password,
                 smtp_server,
                 smtp_port,
                 to_addr_list,
                 title,
                 content,
                 from_name=''):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(title).encode()
    if from_name == '': from_name = from_addr
    msg['From'] = from_name
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr_list, msg.as_string())
    server.quit()
