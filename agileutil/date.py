#coding=utf-8

import datetime
import time


def today():
    return datetime.date.today()


def lastday():
    return str(today() - datetime.timedelta(1))


def tommorrow():
    return today() + datetime.timedelta(1)


def stamp_to_date_str(stamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(stamp)))


def date_str_to_stamp(dateString):
    dateString = str(dateString)
    return int(time.mktime(time.strptime(dateString, '%Y-%m-%d %H:%M:%S')))


def current_time():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def datestr_to_zh_time(date_str):
    '''
    如果时间格式是一天之内的，原样返回
    否则返回1 天前，2 天前，3 天前 这种
    '''
    date_str = str(date_str)
    stamp = date_str_to_stamp(date_str)
    lastdaystr = lastday() + ' 23:59:59'
    lastdaystamp = date_str_to_stamp(lastdaystr)
    if stamp > lastdaystamp:
        return date_str
    else:
        diff = lastdaystamp - stamp
        days = diff / (3600 * 24) + 1
        return str(days) + ' 天前'
