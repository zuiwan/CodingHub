#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.celery_util import make_celery
from Application.app import flask_app

celery_app = make_celery(flask_app)

from flask_sqlalchemy import SQLAlchemy

orm = SQLAlchemy(flask_app)


# 集成度不是很高的应用扩展，即不一定需要相关依赖，需要手动调用获得
def GetMongoConnection():
    from flask_pymongo import PyMongo
    mongo = PyMongo(flask_app)
    return mongo


# from flask_redis import FlaskRedis
# rdb = FlaskRedis(flask_app, strict=True, config_prefix="redis")
def GetRedisConnection(c="persis"):
    from redis import Redis
    RedisBrokerHost = "test.dl.russellcloud.com"
    RedisBrokerPort = 6380
    RedisPersisHost = "api.cannot.cc"
    RedisPersisPort = 6380
    RedisHostDict = dict(persis=RedisPersisHost, broker=RedisBrokerHost)
    RedisPortDict = dict(persis=RedisPersisPort, broker=RedisBrokerPort)
    rdb = Redis(host=RedisHostDict[c], port=RedisPortDict[c])
    return rdb


def GetMysqlEngineAndDBSession():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    # 初始化数据库连接:
    MysqlEngine = create_engine('mysql+mysqlconnector://root:RussellCloud2017@localhost:3306/Russell')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=MysqlEngine)
    return MysqlEngine, DBSession
