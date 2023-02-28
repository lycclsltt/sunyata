"""
PYPI publish
"""

import sys
import subprocess
import platform

binExec = 'python'
system = platform.system()
if platform.python_version()[0:1] == '3' and system == 'Linux':
    binExec = 'python3'

if len(sys.argv) != 3:
    print('Usage:')
    print('%s upload.py [username] [password]' % binExec)
    sys.exit(1)

cmdList = [
    "rm -rf ./pyx.egg-info", "rm -rf ./dist",
    "%s setup.py sdist" % binExec,
    "%s -m twine upload -u '%s' -p '%s' dist/*" %
    (binExec, sys.argv[1], sys.argv[2]), "rm -rf ./pyx.egg-info",
    "rm -rf ./dist"
]

for cmd in cmdList:
    print(cmd)
    _, output = subprocess.getstatusoutput(cmd)
    print(output)