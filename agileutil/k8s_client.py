#coding=utf-8

import requests
import ujson


class K8sClient:

    STRAGE_ROLLING_UPDATE = 'RollingUpdate'
    STRAGE_RECREATE = 'Recreate'
    STRAGE_DEFAULT = 'RollingUpdate'

    PROTOCOL_TCP = 'TCP'
    PROTOCOL_UDP = 'UDP'
    PROTOCOL_SCTP = 'SCTP'

    def __init__(self, baseUrl, token='', timeout=10):
        if baseUrl[-1] == '/': baseUrl[-1] = ''
        self.baseUrl = baseUrl
        self.token = token
        self.headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        self.verify = False
        self.timeout = timeout

    def createNamespace(self, namespace):
        '''
        创建namespace
        参考:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.13/#namespace-v1-core
        https://kubernetes.io/docs/tasks/administer-cluster/namespaces/
        '''
        url = self.baseUrl + '/api/v1/namespaces'
        body = {
            'apiVersion': "v1",
            'kind': 'Namespace',
            'metadata': {
                'name': namespace,
                'labels': {
                    'name': namespace,
                }
            }
        }
        r = requests.post(url,
                          headers=self.headers,
                          data=ujson.dumps(body),
                          verify=self.verify,
                          timeout=self.timeout)
        return r.status_code, r.text

    def deleteNamespace(self, namespace):
        '''
        删除namespace
        '''
        url = self.baseUrl + '/api/v1/namespaces/%s' % namespace
        r = requests.delete(url, headers=self.headers, verify=self.verify)
        return r.status_code, r.text

    def getNamespace(self, namespace):
        '''
        获取一个namespace
        '''
        url = self.baseUrl + '/api/v1/namespaces/%s' % namespace
        r = requests.get(url,
                         headers=self.headers,
                         verify=self.verify,
                         timeout=self.timeout)
        return r.status_code, r.text

    def listNamespace(self):
        '''
        获取所有namespace
        '''
        url = self.baseUrl + '/api/v1/namespaces'
        r = requests.get(url,
                         headers=self.headers,
                         verify=self.verify,
                         timeout=self.timeout)
        return r.status_code, r.text

    def getPods(self, namespace='default', labelSelector={}):
        #获取某个namespace下的pod列表，默认选择default的
        url = self.baseUrl + '/api/v1/namespaces/%s/pods/' % namespace
        if type(labelSelector) == dict and len(labelSelector) != 0:
            queryList = []
            for k, v in labelSelector.items():
                queryList.append('%s=%s' % (k, v))
            queryString = ','.join(queryList)
            url = url + '?labelSelector=' + queryString
        r = requests.get(url,
                         headers=self.headers,
                         verify=self.verify,
                         timeout=self.timeout)
        return r.status_code, r.text

    @classmethod
    def makeDeploymentBody(cls,
                           deployment,
                           env,
                           image='ubuntu:16.04',
                           portList=[],
                           namespace='default',
                           replicas=0,
                           minReadySeconds=0,
                           paused=False,
                           progressDeadlineSeconds=600,
                           revisionHistoryLimit=100,
                           strategy=STRAGE_DEFAULT):
        body = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': deployment,
                'namespace': namespace,
            },
            'spec': {
                'minReadySeconds': minReadySeconds,
                'paused': paused,
                'progressDeadlineSeconds': progressDeadlineSeconds,
                'replicas': replicas,
                'revisionHistoryLimit': revisionHistoryLimit,
                'selector': {
                    'matchLabels': {
                        'app': deployment,  #这里和服务名称一致
                        'env': env,  #这里和环境名称一致(sep, rc, release, prod)
                    },
                },
                'strategy': {
                    'type': strategy
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': deployment,
                            'env': env
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': deployment,
                            'image': image,
                            'ports': portList
                        }]
                    }
                }
            }
        }

        return body

    def createDeployment(self,
                         deployment,
                         env,
                         image='ubuntu:16.04',
                         portList=[],
                         namespace='default',
                         replicas=0,
                         minReadySeconds=0,
                         paused=False,
                         progressDeadlineSeconds=600,
                         revisionHistoryLimit=100,
                         strategy=STRAGE_DEFAULT):
        '''
        创建deployment
        参考：
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.13/#deployment-v1-apps

        参数:
        namespace: 创建属于哪个namespace的deployment
        deployment: deployment名称, 传递时和容器服务名称一致,会被存放到matchlabels中
        replicas: 副本数，默认为0
        minReadySeconds: 可用状态的最小秒数。默认是0（Pod在ready后就会被认为是可用状态
        paused: boolean值, 用来指定暂停和恢复Deployment, 默认False
        progressDeadlineSeconds: 表示Deployment controller等待多少秒才能确定（通过 Deployment status）Deployment进程是卡住的。根据k8s官方，默认为600s
        revisionHistoryLimit: kubectl apply 每次更新应用时 Kubernetes 都会记录下当前的配置，保存为一个 revision（版次），这样就可以回滚到某个特定 revision。默认配置下，Kubernetes 只会保留最近的几个 revision，可以在 Deployment 配置文件中通过 revisionHistoryLimit 属性增加 revision 数量。这里默认设为100.
        strategy: 指定新的Pod替换旧的Pod的策略, Recreate 或 RollingUpdate, 默认为RollingUpdate.Recreate时，在创建出新的Pod之前会先杀掉所有已存在的Pod.
        image: pod运行的镜像
        portList:[ {'name' : 'xxx', 'protocol' : 'TCP/UDP/SCTP', 'hostPort':80, 'hostIP':'0.0.0.0', 'containerPort':80} ] 端口列表

        env:属于哪个环境, sep, rc, release, prod, 会被存放到matchlabels中

        返回:
        状态码，输出, map, json string
        '''
        url = self.baseUrl + '/apis/apps/v1/namespaces/%s/deployments' % namespace

        body = K8sClient.makeDeploymentBody(deployment, env, image, portList,
                                            namespace, replicas,
                                            minReadySeconds, paused,
                                            progressDeadlineSeconds,
                                            revisionHistoryLimit, strategy)

        r = requests.post(url,
                          headers=self.headers,
                          data=ujson.dumps(body),
                          verify=self.verify,
                          timeout=self.timeout)
        return r.status_code, r.text, body, ujson.dumps(body)

    @classmethod
    def makePodBody(cls,
                    podName,
                    image,
                    namespace='default',
                    labels={},
                    annotations={},
                    nodeName='',
                    containerName='',
                    ports=[],
                    command=[]):
        body = {
            'apiVersion': "v1",
            'kind': 'Pod',
            'metadata': {
                'name': podName,
                'namespace': namespace,
                'labels': labels,
                'annotations': annotations,
            },
            'spec': {
                'containers': [{
                    'name': containerName,
                    'image': image,
                    'ports': ports,
                    'command': command,
                }]
            }
        }

        if nodeName != '':
            body['spec']['nodeName'] = nodeName

        if containerName == '':
            body['spec']['containers'][0]['name'] = podName

        return body

    def createPod(self,
                  podName,
                  image,
                  namespace='default',
                  labels={},
                  annotations={},
                  nodeName='',
                  containerName='',
                  ports=[],
                  command=[]):
        url = self.baseUrl + '/api/v1/namespaces/%s/pods' % namespace

        body = K8sClient.makePodBody(podName, image, namespace, labels,
                                     annotations, nodeName, containerName,
                                     ports, command)

        r = requests.post(url,
                          headers=self.headers,
                          data=ujson.dumps(body),
                          verify=self.verify,
                          timeout=self.timeout)
        return r.status_code, r.text, body, ujson.dumps(body)

    def deletePod(self, podName, namespace='default'):
        url = self.baseUrl + '/api/v1/namespaces/%s/pods/%s' % (namespace,
                                                                podName)
        r = requests.delete(url,
                            headers=self.headers,
                            verify=self.verify,
                            timeout=self.timeout)
        return r.status_code, r.text

    def replacePod(self, podName, podBody, namesapce='default'):
        url = self.baseUrl + '/api/v1/namespaces/%s/pods/%s' % (namesapce,
                                                                podName)
        r = requests.put(url,
                         data=podBody,
                         headers=self.headers,
                         verify=self.verify,
                         timeout=self.timeout)
        return r.status_code, r.text

    def getPod(self, podName, namespace='default'):
        url = self.baseUrl + '/api/v1/namespaces/%s/pods/%s' % (namespace,
                                                                podName)
        r = requests.get(url,
                         headers=self.headers,
                         verify=self.verify,
                         timeout=self.timeout)
        return r.status_code, r.text

    def getPodStatus(self, pod):
        '''
        成功返回状态字符串，None
        失败返回'', 错误信息
        '''
        status = pod['status']
        ret = ''

        print(status)

        try:
            if pod['status']['containerStatuses'][0]['ready'] == True:
                ret = pod['status']['phase']
            else:
                stateMap = pod['status']['containerStatuses'][0]['state']
                for state, desc in stateMap.items():
                    ret = desc['reason']
                    break
        except Exception as ex:
            return ret, str(ex)
        return ret, None


'''
#get pod status
token = """eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJlY2RhdGFhcGktdG9rZW4tdmZyY24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZWNkYXRhYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNzFlOWViOTMtZTYzYy0xMWU4LTk5ZTUtNzgyYmNiNTkwNTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmVjZGF0YWFwaSJ9.Q_M4WLYmMWEUGcNwdt6fRpIWGhjAGsabXUWOzthuluUBb_jgKFDF4P0bvqq2gHe0mVePw-wrtCtnHIXEhHptT_SskstGb3AlyePlh0_4ixsVoS6R10ksnEbk_BdC1AU18Yq3A4MQ2f8-NivKddok8HyTRN-wXe5Ilw7ion7ZeU7RFvk-PSqV_QsnFThdiyPy1cGeDj0VWBu9ceSExsR5L879w6YwJMbqUFePYsxqSVjrJ2o7WrqLDb_fdlQGG50qFOYdVj9iTXj_mCEQHw9Xxv6KNWTDaIYpFxrrItYnnLT3wAYp0z_K2Qi4ruiQpc14-snGOD1FgJGh6IzUN_lSKg"""
cli = K8sClient(baseUrl = 'https://10.12.35.3:6443', token = token)
code, resp = cli.getPod('pod-10-20-0-130', 'sce')
pod = ujson.loads(resp)
status, err = cli.getPodStatus(pod)
print('status:', status)
print('err:', err)
'''
'''
{
	'phase': 'Running',
	'conditions': [{
		'type': 'Initialized',
		'status': 'True',
		'lastProbeTime': None,
		'lastTransitionTime': '2018-12-28T07:47:20Z'
	}, {
		'type': 'Ready',
		'status': 'True',
		'lastProbeTime': None,
		'lastTransitionTime': '2018-12-28T07:47:23Z'
	}, {
		'type': 'ContainersReady',
		'status': 'True',
		'lastProbeTime': None,
		'lastTransitionTime': '2018-12-28T07:47:23Z'
	}, {
		'type': 'PodScheduled',
		'status': 'True',
		'lastProbeTime': None,
		'lastTransitionTime': '2018-12-28T07:47:20Z'
	}],
	'hostIP': '10.12.35.2',
	'podIP': '10.20.0.130',
	'startTime': '2018-12-28T07:47:20Z',
	'containerStatuses': [{
		'name': 'container-10-20-0-130',
		'state': {
			'running': {
				'startedAt': '2018-12-28T07:47:22Z'
			}
		},
		'lastState': {},
		'ready': True,
		'restartCount': 0,
		'image': '10.12.35.2/sce/sce-go-test:go-9ba6ba10-prod-1545892604',
		'imageID': 'docker-pullable://10.12.35.2/sce/sce-go-test@sha256:d148ed2775692453da324ca7662b9af87319d126ef92a2d040a6d9727263392f',
		'containerID': 'docker://056dfa639d8806089bcfee1b9ca6a4fd5b97ebb1e023b338b435cc7e1f0f8c35'
	}],
	'qosClass': 'BestEffort'
}
'''
'''
token = """eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJlY2RhdGFhcGktdG9rZW4tdmZyY24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZWNkYXRhYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNzFlOWViOTMtZTYzYy0xMWU4LTk5ZTUtNzgyYmNiNTkwNTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmVjZGF0YWFwaSJ9.Q_M4WLYmMWEUGcNwdt6fRpIWGhjAGsabXUWOzthuluUBb_jgKFDF4P0bvqq2gHe0mVePw-wrtCtnHIXEhHptT_SskstGb3AlyePlh0_4ixsVoS6R10ksnEbk_BdC1AU18Yq3A4MQ2f8-NivKddok8HyTRN-wXe5Ilw7ion7ZeU7RFvk-PSqV_QsnFThdiyPy1cGeDj0VWBu9ceSExsR5L879w6YwJMbqUFePYsxqSVjrJ2o7WrqLDb_fdlQGG50qFOYdVj9iTXj_mCEQHw9Xxv6KNWTDaIYpFxrrItYnnLT3wAYp0z_K2Qi4ruiQpc14-snGOD1FgJGh6IzUN_lSKg"""
cli = K8sClient(baseUrl = 'https://10.12.35.3:6443', token = token)
code, resp = cli.getPods(namespace='sce', labelSelector={'app':'sce-java-test', 'env' : 'prod'})
print(code)
print(resp)
'''
'''
#get pod
token = """eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJlY2RhdGFhcGktdG9rZW4tdmZyY24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZWNkYXRhYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNzFlOWViOTMtZTYzYy0xMWU4LTk5ZTUtNzgyYmNiNTkwNTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmVjZGF0YWFwaSJ9.Q_M4WLYmMWEUGcNwdt6fRpIWGhjAGsabXUWOzthuluUBb_jgKFDF4P0bvqq2gHe0mVePw-wrtCtnHIXEhHptT_SskstGb3AlyePlh0_4ixsVoS6R10ksnEbk_BdC1AU18Yq3A4MQ2f8-NivKddok8HyTRN-wXe5Ilw7ion7ZeU7RFvk-PSqV_QsnFThdiyPy1cGeDj0VWBu9ceSExsR5L879w6YwJMbqUFePYsxqSVjrJ2o7WrqLDb_fdlQGG50qFOYdVj9iTXj_mCEQHw9Xxv6KNWTDaIYpFxrrItYnnLT3wAYp0z_K2Qi4ruiQpc14-snGOD1FgJGh6IzUN_lSKg"""
cli = K8sClient(baseUrl = 'https://10.12.35.3:6443', token = token)
code, resp = cli.getPod('lyc-test-pod-16', 'sce')
print(code, resp)
'''
'''
#replace pod
podBody = K8sClient.makePodBody(
    podName = 'lyc-test-pod-12', 
    image = 'nginx:1.7.9', 
    namespace='sce',
    labels = {
        'env' : 'sep',
        'app' : app,
    },
    annotations = {
        'cni.projectcalico.org/ipAddrs' : "[\"10.20.35.8\"]"
    },
    nodeName = 'bjxg-ap-35-2',
    containerName = 'lyc-test-container-12',
    ports = [
        {
            'containerPort' : 81,
        }
    ]
)

podBody = """{"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{"cni.projectcalico.org/ipAddrs":"['10.20.35.9']"},"labels":{"app":"lyctest","env":"sep"},"name":"lyc-test-pod-13"},"spec":{"containers":[{"command":[],"image":"nginx:1.7.9","name":"lyc-test-container-13","ports":[{"containerPort":81}]}],"nodeName":"bjxg-ap-35-2"}}"""
code, resp = cli.replacePod(
    podName = 'lyc-test-pod-13',
    podBody = podBody,
    namesapce= 'sce'
)
print(podBody)
print(code)
print(resp)
'''
'''
#delete pod
token = """eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJlY2RhdGFhcGktdG9rZW4tdmZyY24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZWNkYXRhYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNzFlOWViOTMtZTYzYy0xMWU4LTk5ZTUtNzgyYmNiNTkwNTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmVjZGF0YWFwaSJ9.Q_M4WLYmMWEUGcNwdt6fRpIWGhjAGsabXUWOzthuluUBb_jgKFDF4P0bvqq2gHe0mVePw-wrtCtnHIXEhHptT_SskstGb3AlyePlh0_4ixsVoS6R10ksnEbk_BdC1AU18Yq3A4MQ2f8-NivKddok8HyTRN-wXe5Ilw7ion7ZeU7RFvk-PSqV_QsnFThdiyPy1cGeDj0VWBu9ceSExsR5L879w6YwJMbqUFePYsxqSVjrJ2o7WrqLDb_fdlQGG50qFOYdVj9iTXj_mCEQHw9Xxv6KNWTDaIYpFxrrItYnnLT3wAYp0z_K2Qi4ruiQpc14-snGOD1FgJGh6IzUN_lSKg"""
cli = K8sClient(baseUrl = 'https://10.12.35.3:6443', token = token)
code, resp = cli.deletePod('lyc-test-pod-11', 'sce')
print(code, resp)
'''
'''
#create pod
token = """eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJlY2RhdGFhcGktdG9rZW4tdmZyY24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZWNkYXRhYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNzFlOWViOTMtZTYzYy0xMWU4LTk5ZTUtNzgyYmNiNTkwNTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmVjZGF0YWFwaSJ9.Q_M4WLYmMWEUGcNwdt6fRpIWGhjAGsabXUWOzthuluUBb_jgKFDF4P0bvqq2gHe0mVePw-wrtCtnHIXEhHptT_SskstGb3AlyePlh0_4ixsVoS6R10ksnEbk_BdC1AU18Yq3A4MQ2f8-NivKddok8HyTRN-wXe5Ilw7ion7ZeU7RFvk-PSqV_QsnFThdiyPy1cGeDj0VWBu9ceSExsR5L879w6YwJMbqUFePYsxqSVjrJ2o7WrqLDb_fdlQGG50qFOYdVj9iTXj_mCEQHw9Xxv6KNWTDaIYpFxrrItYnnLT3wAYp0z_K2Qi4ruiQpc14-snGOD1FgJGh6IzUN_lSKg"""
cli = K8sClient(baseUrl = 'https://10.12.35.3:6443', token = token)
'''
'''
app = 'lyctest'
code, resp, body, json = cli.createPod(
    podName = 'lyc-test-pod-15', 
    image = 'nginx:1.7.9', 
    namespace='sce',
    labels = {
        'env' : 'sep',
        'app' : app,
    },
    annotations = {
        'cni.projectcalico.org/ipAddrs' : "[\"10.20.35.11\"]"
    },
    nodeName = 'bjxg-ap-35-2',
    containerName = 'lyc-test-container-15',
    ports = [
        {
            'containerPort' : 81,
        }
    ]
)
print(code)
print(resp)
print(json)
'''
'''
#create deployment
token = """eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJlY2RhdGFhcGktdG9rZW4tdmZyY24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZWNkYXRhYXBpIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNzFlOWViOTMtZTYzYy0xMWU4LTk5ZTUtNzgyYmNiNTkwNTcwIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmVjZGF0YWFwaSJ9.Q_M4WLYmMWEUGcNwdt6fRpIWGhjAGsabXUWOzthuluUBb_jgKFDF4P0bvqq2gHe0mVePw-wrtCtnHIXEhHptT_SskstGb3AlyePlh0_4ixsVoS6R10ksnEbk_BdC1AU18Yq3A4MQ2f8-NivKddok8HyTRN-wXe5Ilw7ion7ZeU7RFvk-PSqV_QsnFThdiyPy1cGeDj0VWBu9ceSExsR5L879w6YwJMbqUFePYsxqSVjrJ2o7WrqLDb_fdlQGG50qFOYdVj9iTXj_mCEQHw9Xxv6KNWTDaIYpFxrrItYnnLT3wAYp0z_K2Qi4ruiQpc14-snGOD1FgJGh6IzUN_lSKg"""
cli = K8sClient(baseUrl = 'https://10.12.35.3:6443', token = token)
code, resp, body, jsonStr = cli.createDeployment(
    namespace = 'sce',
    deployment = 'test-intf12',
    replicas = 2,
    env = 'prod',
    portList = [
        {
            'name' : 'testddrda-port1',
            'protocol' : K8sClient.PROTOCOL_TCP,
            'hostPort' : 80,
            'hostIP' : '0.0.0.0',
            'containerPort' : 80,
        }
    ]
)
print(code)
print(resp)
print('body:', body)
print('json str:', jsonStr)
'''
