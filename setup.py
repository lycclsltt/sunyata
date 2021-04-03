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

DEFINE_VERSION = '0.0.12'
from setuptools import setup
import platform
system = platform.system()
webpy = 'web.py'
if platform.python_version()[0:1] == '3':
    webpy = 'web.py==0.40.dev1'
requireList = [
    'lz4==3.1.3',
    'requests==2.25.1',
    'PyMySQL==0.10.1',
    'DBUtils==1.3', 
    'sanic==20.12.2',
]
#if requireList == 'Linux':
#    requireList.append('japronto')
#    requireList.append('sanic')

setup(name='agileutil',
      version=DEFINE_VERSION,
      description='Light, simple RPC framework for Python',
      author='tank',
      license='MIT',
      platforms="any",
      install_requires=requireList,
      classifiers=[
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
