#coding=utf-8
'''
压力测试时使用
locust -f locust_demo.py
'''

from locust import HttpLocust, TaskSet, task, between


class WebsiteTasks(TaskSet):
    @task
    def test(self):
        self.client.get("/hello")


class WebsiteUser(HttpLocust):
    host = "http://144.34.213.205:10001"  #被测系统的host
    task_set = WebsiteTasks  #该类定义用户任务信息，该类继承TaskSet
    wait_time = between(1000, 2000)
    stop_timeout = 30
