#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.celery_util import make_celery
from Application.app import flask_app

celery_app = make_celery(flask_app)

from flask_sqlalchemy import SQLAlchemy

orm = SQLAlchemy(flask_app)

from flask_pymongo import PyMongo

mongo = PyMongo(flask_app)

# from flask_redis import FlaskRedis
# rdb = FlaskRedis(flask_app, strict=True, config_prefix="redis")
HOST = "test.dl.russellcloud.com"
RedisHost = HOST
RedisPort = 6380
import redis

rdb = redis.Redis(host=RedisHost, port=RedisPort)

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker

# 初始化数据库连接:
MysqlEngine = create_engine('mysql+mysqlconnector://root:RussellCloud2017@localhost:3306/Russell')
# 创建DBSession类型:
DBSession = sessionmaker(bind=MysqlEngine)
