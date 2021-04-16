DEFINE_VERSION = '0.0.18'
from setuptools import setup

requireList = [
    'lz4==3.1.3',
    'requests==2.25.1',
    'PyMySQL==0.10.1',
    'DBUtils==1.3',
    'sanic==20.12.3',
]

setup(
    name='agileutil',
    version=DEFINE_VERSION,
    description='Light, simple, asynchronous RPC framework for Python',
    author='tank',
    license='MIT',
    platforms="any",
    install_requires=requireList,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='agileutil',
    packages=['agileutil', 'agileutil/rpc', 'agileutil/algorithm', 'agileutil/cli'],
    include_package_data=True,
    entry_points = {
        'console_scripts' : [
            'agileutil=agileutil.cli.entry:main'
        ]
    }
)
