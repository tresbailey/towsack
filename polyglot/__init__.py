
import json
import logging
import os
import socket
import uuid
from bson.errors import InvalidId
from flask import Flask
from flaskext.mongoalchemy import MongoAlchemy
from flask.ext.principal import Principal, Permission, RoleNeed
from flask.ext.sqlalchemy import SQLAlchemy
from gridfs import GridFS
from logging import handlers
from flask_redis import Redis


handler = logging.handlers.RotatingFileHandler("polyglot.log")
log = logging.getLogger('polyglot')
log.setLevel("DEBUG")
#log.addHandler( handler)

APP = Flask(__name__)
APP.secret_key = str(uuid.uuid1())



APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://docker:docker@192.168.59.103:49155/docker'
APP.config['REDIS_URL'] = "redis://localhost:6379/3"
APP.config['REDIS_HASH_FBN'] = 'field_by_name'

DB = SQLAlchemy(APP)

MEM = Redis(APP)

HOME_URL = os.getenv('HOST', 'http://localhost')

LOCAL_SERVER = not socket.gethostname().endswith('.w10')

from flask.ext.login import LoginManager

LM = LoginManager()
LM.init_app(APP)
principals = Principal(APP)


from polyglot.rest.handlers import errors
APP.register_blueprint(errors)
from polyglot.rest.meta import meta
APP.register_blueprint(meta)
from polyglot.rest.instance import instances
APP.register_blueprint(instances)

if __name__ == '__main__':
    APP.run('127.0.0.1', threaded=True)
