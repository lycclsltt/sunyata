#coding=utf-8
'''
required ansible version <= 2.0
'''

import ansible.runner
import json


def run(module_name,
        module_args='',
        forks=1,
        host_list=[],
        ssh_user='',
        ssh_pass=''):
    runner = ansible.runner.Runner(module_name=module_name,
                                   module_args=module_args,
                                   forks=forks,
                                   host_list=host_list,
                                   extra_vars={
                                       "ansible_ssh_user": ssh_user,
                                       "ansible_ssh_pass": ssh_pass
                                   })
    datastructure = runner.run()
    return json.dumps(datastructure)
