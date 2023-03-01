DEFINE_VERSION = '0.0.29'
from setuptools import setup

requireList = [
    'lz4==3.1.3',
    'requests==2.25.1',
    'PyMySQL==0.10.1',
    'DBUtils==1.3',
]

setup(
    name='sunyata',
    version=DEFINE_VERSION,
    description='Light, simple, asynchronous RPC framework for Python',
    author='tank',
    license='MIT',
    platforms="any",
    install_requires=requireList,
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='sunyata',
    packages=[
        'sunyata', 
        'sunyata/rpc', 
        'sunyata/algorithm', 
        'sunyata/cli',
        'sunyata/http'
    ],
    include_package_data=True,
    entry_points = {
        'console_scripts' : [
            'sunyata=sunyata.cli.entry:main'
        ]
    }
)
