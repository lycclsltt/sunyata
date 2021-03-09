#coding=utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import socket
import traceback


class MailServerConfig(object):

    def __init__(self, mailHost, mailPort, mailUser, mailPass, timeout = 30):
        self.mailHost = mailHost
        self.mailPort = mailPort
        self.mailUser = mailUser
        self.mailPass = mailPass
        self.timeout = timeout


class MailMeta(object):

    def __init__(self, sender, receiver, subject, html, pic = None):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.html = html
        self.pic = pic
        self.message = None

    def getMessage(self):
        if self.message == None:
            message = MIMEMultipart()
            message['Subject'] = Header(self.subject, 'utf-8').encode()
            message['From'] = Header(self.sender, 'utf-8').encode()
            if self.pic:
                f = open(self.pic, 'rb')
                msgImage = MIMEImage(f.read())
                f.close()
                msgImage.add_header('Content-ID', 'pic')
                msgImage["Content-Disposition"] = 'attachment; filename="pic.png"'
                message.attach(msgImage)
            message.attach(MIMEText(self.html, 'html', 'utf-8'))
            self.message = message
        return self.message.as_string()



class MailSender(object):

    def __init__(self, mailServerConf):
        self.mailServerConfig = mailServerConf

    def send(self, mail):
        '''
        :param mail: MailMeta obj
        :return: 成功返回None, 否则返回错误信息
        '''
        try:
            socket.setdefaulttimeout(self.mailServerConfig.timeout)
            smtpObj = smtplib.SMTP(host=self.mailServerConfig.mailHost, port=self.mailServerConfig.mailPort)
            smtpObj.ehlo()  #发送SMTP 'ehlo' 命令
            smtpObj.starttls()
            smtpObj.login(self.mailServerConfig.mailUser, self.mailServerConfig.mailPass)
            smtpObj.sendmail(from_addr=mail.sender, to_addrs=mail.receiver, msg=mail.getMessage())
            smtpObj.quit()
            return None
        except Exception as ex:
            return str(ex) + traceback.format_exc()