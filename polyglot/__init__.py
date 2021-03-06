
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



APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@%s:%s/%s' % (os.getenv('PG_USER'), os.getenv('PG_PASS'), 'pg', os.getenv('PG_PORT'), os.getenv('PG_DBNAME'))
APP.config['REDIS_URL'] = "redis://%s:%s/3" % (os.getenv('REDIS_HOST', 'localhost'), os.getenv('REDIS_PORT', '6379'))
APP.config['REDIS_HASH_FBN'] = 'field_by_name'

DB = SQLAlchemy(APP)

MEM = Redis(APP)

HOME_URL = os.getenv('HOST', 'http://localhost')

LOCAL_SERVER = not socket.gethostname().endswith('.w10')

from flask.ext.login import LoginManager

LM = LoginManager()
LM.init_app(APP)
principals = Principal(APP)

from polyglot.rest.meta import meta
APP.register_blueprint(meta)
from polyglot.rest.instance import instances
APP.register_blueprint(instances)
from polyglot.rest.validations import val_funks
APP.register_blueprint(val_funks)
from polyglot.rest.handlers import handle_not_found, handle_excpetions, handle_bad_id

if __name__ == '__main__':
    APP.run('127.0.0.1', threaded=True)
