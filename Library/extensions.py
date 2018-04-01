#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.celery_util import make_celery
from Application.app import flask_app

celery_app = make_celery(flask_app)

from flask_sqlalchemy import SQLAlchemy
orm = SQLAlchemy(flask_app)

from flask_pymongo import PyMongo
mongo = PyMongo(flask_app)

from flask_redis import FlaskRedis
rdb = FlaskRedis(flask_app)