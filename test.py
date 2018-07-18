# -*- coding: utf-8 -*-
from datetime import datetime

from celery import Celery
from pika import BlockingConnection, ConnectionParameters, BasicProperties, exceptions
import time
from flask import Flask, render_template

# Flask configure
app = Flask(__name__)


# celery configure
def make_celery(app):
    celery = Celery('test',
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND']
                    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='amqp://guest:guest@10.237.43.101/net_test',
    CELERY_RESULT_BACKEND='redis://:travelskyopenstackcloud@10.237.43.105:6379/0'
)
celery = make_celery(app)


# 同步接口
@app.route('/sync')
def sync():
    print u'前端发送同步请求'
    time.sleep(2)
    send_msg.apply_async()
    return u'同步操作执行中！'

# mq configuration
mq_host = '127.0.0.1'
mq_port = 5672
queue = 'push_queue1'


def _get_conn(host=mq_host, port=mq_port):
    return BlockingConnection(ConnectionParameters(host=host, port=port))


def send(msgs, queue_name=queue):
    conn = _get_conn()
    chan = conn.channel()
    chan.confirm_delivery()
    # chan.exchange_declare(exchange=exchange_name, type='direct', passive=False, durable=True, auto_delete=False)
    chan.queue_declare(queue=queue_name, durable=True, exclusive=False, auto_delete=False)  # a synchronous call
    # chan.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
    try:
        for msg in msgs:
            chan.basic_publish(exchange='', routing_key=queue_name, body=msg.encode('utf-8'),
                               mandatory=True,
                               properties=BasicProperties(delivery_mode=2, content_type='application/json'))
            print '[x] Sent msg:%s' % msg
    except exceptions.ConnectionClosed as exc:
        print 'Error. Publisher RabbitMQ_Conn closed when sending messages...'
    finally:
        conn.close()


# celery任务
@celery.task
def send_msg():
    time.sleep(10)
    msgs = [u'{"msg": u"同步完成", "time": u":' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + u'"}']
    send(msgs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
