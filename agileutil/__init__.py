import sys
try:
    from imp import reload
except:
    pass
reload(sys)
try:
    sys.setdefaultencoding("utf-8")
except:
    pass
