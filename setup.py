#!/usr/bin/env python
'''
pub.sh

#!/bin/sh
rm -rf ./agileutil.egg-info
rm -rf ./build
rm -rf ./dist
rm -rf ./*.tar.gz
python setup.py sdist
twine upload -u [username] -p [password] dist/*
python setup.py install
'''

DEFINE_VERSION = '0.0.2'
from setuptools import setup
import platform
system = platform.system()
webpy = 'web.py'
if platform.python_version()[0:1] == '3':
    webpy = 'web.py==0.40.dev1'
requireList = [
    'pexpect', 'ujson', 'requests', 'python-decouple', 'PyMySQL==0.10.1',
    'DBUtils==1.3', 'IPy', 'sanic==20.12.2'
]
#if requireList == 'Linux':
#    requireList.append('japronto')
#    requireList.append('sanic')

setup(name='agileutil',
      version=DEFINE_VERSION,
      description='Python3 RPC Framework',
      author='tank',
      license='MIT',
      platforms="any",
      install_requires=requireList,
      classifiers=[
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      keywords='agileutil',
      packages=['agileutil', 'agileutil/rpc', 'agileutil/algorithm'],
      include_package_data=True)
