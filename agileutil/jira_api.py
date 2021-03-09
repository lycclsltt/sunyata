#coding=utf-8
'''
这里调用jira api创建issue
参考:
https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
https://developer.atlassian.com/cloud/jira/platform/rest/#api-api-2-issue-issueIdOrKey-transitions-post

curl -D- -u 用户名:密码 -X POST --data '{"fields": {"project":{ "key": "OP"},"summary": "jira api test","description": "create issue test","components":[{"name":"MySQL"}], "issuetype": {"name":"任务"}}}' -H "Content-Type: application/json" http://xxxxx/rest/api/2/issue/
'''

import requests
import ujson


def create_issue(url,
                 username,
                 password,
                 project_key='OP',
                 issuetype=u'任务',
                 components='MySQL',
                 summary='',
                 description=''):
    '''
    url: http://xxxxxx/rest/api/2/issue/
    '''
    headers = {'Content-Type': 'application/json'}
    params = {
        'fields': {
            'project': {
                'key': project_key
            },
            'summary': summary,
            'components': [{
                'name': components
            }],
            'description': description,
            'issuetype': {
                "name": issuetype
            }
        }
    }
    params = ujson.dumps(params)
    s = requests.Session()
    s.headers.update(headers)
    s.auth = (username, password)
    r = s.post(url, data=params)
    return r.status_code, r.text


def reslove_issue(url, username, password, issue_key, trans_id):
    '''
    url: https://xxxx/rest/api/2/issue/issueIdOrKey/transitions
    '''
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    params = {'transition': {'id': trans_id}}
    params = ujson.dumps(params)
    s = requests.Session()
    s.headers.update(headers)
    s.auth = (username, password)
    url = url.replace('issueIdOrKey', issue_key)
    r = s.post(url, data=params)
    return r.status_code, r.text
