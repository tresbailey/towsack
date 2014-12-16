from __future__ import absolute_import
from celery import Celery
import os

app = Celery('<worker name>', 
    broker='<Broker Connection String>',
    backend='redis',
    include=['<module that contains celery task method'])

app.conf.update(BROKER_BACKEND='redis')
app.conf.update(CELERY_ACCEPT_CONTENT=['json', 'msgpack', 'yaml'])

if __name__ == '__main__':
    app.start()
