#coding=utf-8

import os
import re
import sys
import socket
import hashlib
import urllib
try:
    import urllib2
except:
    import urllib as urllib2
import base64
import time
try:
    import commands
except:
    import subprocess as commands
#import sqlparse
import zlib
import platform


def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()


def itoa(ascii_value):
    return chr(ascii_value)


def atoi(char):
    return ord(char)


def exit(text=None):
    if text:
        print(text)
    sys.exit()


def findall(regex, text):
    pattern = re.compile(regex)
    search_result = pattern.findall(text)
    return search_result


def create_standard_daemon():
    if os.fork() > 0:
        sys.exit(0)
    os.chdir('/')
    os.setsid()
    os.umask(0)
    if (os.fork() > 0):
        sys.exit(0)
    return True


def create_simple_daemon():
    if (os.fork() > 0):
        sys.exit(0)
    return True


def execmd(cmdString):
    status, output = commands.getstatusoutput(cmdString)
    return status, output


def http(url, params=None, mtimeout=10, user=None, pwd=None):
    if user and pwd:
        #auth
        base64String = base64.encodestring("%s:%s" % (user, pwd))
        authheader = "Basic %s" % base64String
        request = urllib2.Request(url)
        request.add_header("Authorization", authheader)
        response = urllib2.urlopen(request)
        return response.code, response.read()
    else:
        code = 0
        try:
            data = None
            if params:
                data = urllib.urlencode(params)
            request = urllib2.Request(url, data)
            response = urllib2.urlopen(url=request, timeout=mtimeout)
            return response.code, response.read()
        except Exception as ex:
            return code, str(ex)


def safe_reload(module_name):
    try:
        reload(module_name)
    except Exception as ex:
        pass


def write_file(file, content, is_append=False):
    way = 'w+'
    if is_append:
        way = 'a+'
    try:
        fd = open(file, way)
        fd.write(content)
        fd.close()
        return True
    except:
        return False


def get_file_content(file):
    fd = open(file, 'r')
    file_content = fd.read()
    fd.close()
    return file_content


def download(url, filename):
    """
    download file and save to spefic path 
    """
    try:
        urllib.urlretrieve(url, filename)
    except Exception as ex:
        return False
    return True


def hostname():
    return socket.gethostname()


def local_ip():
    return socket.gethostbyname(socket.gethostname())


def local_ipv4_list():
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    if addrs == None or len(addrs) == 0: return []
    ipv4list = []
    for addr in addrs:
        tuple_element = addr[4]
        ip = tuple_element[0]
        if ':' in ip: continue
        ipv4list.append(ip)
    ipv4list = list(set(ipv4list))
    return ipv4list


def telnet(ip, port, timeout):
    socket.setdefaulttimeout(timeout)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    client.close()
    return True


def proc_num_by_key_word(kwd):
    status, output = execmd("ps auxww | grep %s | grep -v grep | wc -l" % kwd)
    return int(output)


def del_file_before_days(dirname, days):
    if dirname[-1] != '/':
        dirname = dirname + '/'
    f_list = os.listdir(dirname)
    cur_time = time.time()
    for f in f_list:
        abs_path = dirname + f
        modify_time = os.path.getmtime(abs_path)
        time_diff = cur_time - modify_time
        days_diff = (time_diff / 3600) / 24
        if days_diff >= days:
            os.remove(abs_path)


def get_cur_proc_socket_num():
    pid = os.getpid()
    cmd = "ls /proc/%s/fd -l | grep socket: | wc -l" % pid
    _, output = execmd(cmd)
    return int(output.strip())


def file_size(f):
    return os.path.getsize(f)


def add_log_not_roll_event(logfile,
                           cmd_list=[],
                           is_block=False,
                           check_intval=5,
                           exec_intval=1,
                           is_raise_open_file_exception=True):
    ########################################
    def loop_check(logfile,
                   cmd_list=[],
                   check_intval=5,
                   exec_intval=1,
                   is_raise_open_file_exception=True):
        last_size = 0
        while True:
            time.sleep(check_intval)
            size = 0
            try:
                size = file_size(logfile)
            except Exception as ex:
                if is_raise_open_file_exception:
                    raise ex
                else:
                    size = 0
            print('size', size)
            if size == last_size:
                for cmd in cmd_list:
                    time.sleep(exec_intval)
                    os.system(cmd)
            else:
                last_size = size

    ########################################
    if is_block:
        loop_check(logfile, cmd_list, check_intval, exec_intval)
    else:
        pid = os.fork()
        if pid > 0:
            return True
        elif pid < 0:
            return False
        else:
            loop_check(logfile, cmd_list, check_intval, exec_intval)


#def format_sql(sql):
#    if '\n' in sql: return sql
#    formatSqlString = sqlparse.format(sql, reindent=True, keyword_case='upper')
#    return formatSqlString


def compress(string, level=9, encoding='utf-8'):
    if platform.python_version()[0:1] == '3':
        string = string.encode(encoding)
        compress = zlib.compress(string, level)
        return compress
    else:
        return zlib.compress(string)


def decompress(string):
    de_com = zlib.decompress(string)
    return de_com


def list_all_files(dir_path):
    files = []
    l = os.listdir(dir_path)
    for i in range(0, len(l)):
        path = os.path.join(dir_path, l[i])
        if os.path.isdir(path):
            files.extend(list_all_files(path))
        if os.path.isfile(path):
            files.append(path)
    return files


def gen_reqs():
    py_version = ''
    if platform.python_version()[0:1] == '3':
        py_version = 3
    else:
        py_version = ''
    pip = 'pip' + str(py_version)
    cmd = 'source ./bin/activate'
    execmd(cmd)
    cmd = pip + " freeze 2> /dev/null"
    status, output = execmd(cmd)
    lines = output.split("\n")
    lines = list(set(lines))
    try:
        lines.remove('')
    except:
        pass
    pkg_ver_map = {}
    for line in lines:
        pkg, ver = line.split('==')
        pkg_ver_map[pkg] = ver
    include_pkg = []
    all_f = list_all_files('./')
    all_py_f = []
    for f in all_f:
        _, ext = os.path.splitext(f)
        if ext == '.py':
            all_py_f.append(f)
    all_import_lines = []
    for f in all_py_f:
        fp = open(f, 'r')
        lines = fp.readlines()
        fp.close()
        for line in lines:
            if 'import ' in line or 'from ' in line:
                all_import_lines.append(line)
    real_need_imports_map = {}
    for pkg, ver in pkg_ver_map.items():
        tmp_pkg = pkg.replace('python', '').replace('-', '')
        for line in all_import_lines:
            if tmp_pkg in line:
                real_need_imports_map[pkg] = ver
                break
    f = open('./requirements.txt', 'w')
    for pkg, ver in real_need_imports_map.items():
        f.write(pkg + '==' + str(ver) + "\n")
    f.close()


class DebugUtil(object):

    def __init__(self):
        self.tagList = []
        self.curTime = time.time()

    def tag(self, tagName):
        tagName = str(tagName)
        if len(self.tagList) == 0:
            self.tagList.append(tagName)
            self.curTime = time.time()
        else:
            diff = time.time() - self.curTime
            self.curTime = time.time()
            self.tagList.append(round(diff, 3))
            self.tagList.append(tagName)

    def finish(self):
        cost = 0
        for i in self.tagList:
            print(i)
            if type(i) == int or type(i) == float:
                cost = cost + i
        print('total cost:', cost ,' seconds')