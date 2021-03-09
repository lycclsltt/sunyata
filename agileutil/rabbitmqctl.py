#coding=utf-8
'''
producer:
    rbtctl = RabbitmqCtl(
        host = 'xxxxxxxx',
        port = 5672,
        user = 'admin',
        pwd = 'admin',
        vhost = 'common',
        exchange = 'ha_exchange',
        queue = 'test_que',
        routing_key = 'default'
    )
    rbtctl.push('aaaa')
    print rbtctl.pull()
'''

import pika

MSG_PERSISTENT = 2


class RabbitmqCtl:
    def __init__(self,
                 host,
                 port,
                 user,
                 pwd,
                 vhost,
                 exchange,
                 queue,
                 routing_key,
                 durable=True,
                 exchange_type='direct',
                 prefetch_count=1):
        self._host = host
        self._port = port
        self._user = user
        self._pwd = pwd
        self._vhost = vhost
        self._exchange = exchange
        self._queue = queue
        self._routing_key = routing_key
        self._durable = durable
        self._exchange_type = exchange_type
        self._prefetch_count = prefetch_count
        self._credentials = None
        self._params = None
        self._connection = None
        self._channel = None

    def connect(self):
        if self._connection is None:
            self._credentials = pika.PlainCredentials(self._user, self._pwd)
            self._params = pika.ConnectionParameters(self._host, self._port,
                                                     str(self._vhost),
                                                     self._credentials)
            self._connection = pika.BlockingConnection(self._params)
            self._channel = self._connection.channel()
            self._channel.exchange_declare(durable=self._durable,
                                           exchange=self._exchange,
                                           exchange_type=self._exchange_type)
            self._channel.queue_declare(queue=self._queue,
                                        durable=self._durable)
            self._channel.basic_qos(prefetch_count=1)

    def close(self):
        if self._connection:
            self._connection.close()
            self._credentials = None
            self._params = None
            self._connection = None
            self._channel = None

    def push(self, msgBody):
        if self._connection is None: self.connect()

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=msgBody,
            properties=pika.BasicProperties(delivery_mode=MSG_PERSISTENT))

    def pull(self, no_ack_tag=True):
        if self._connection is None: self.connect()
        method, properties, body = self._channel.basic_get(queue=self._queue,
                                                           no_ack=no_ack_tag)
        return body
