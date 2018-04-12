#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask

HOST = "test.dl.russellcloud.com"
RedisHost = HOST
RedisPort = 6380


def create_app(debug=True):
    flask_app = Flask(__name__, static_url_path='/assets',
                      template_folder="templates", static_folder="static")

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://zuiwan:zuiwan2018@localhost:3306/zuiwan'
    flask_app.config['KAFKA_BROKER_URI'] = ['']
    flask_app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    flask_app.config['UPLOAD_WORK_FOLDER'] = "/root/CodingHub/workspace/"
    flask_app.config['UPLOAD_DATA_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "data/"
    flask_app.config['UPLOAD_EXPERIMENT_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "experiment/"
    flask_app.config['UPLOAD_MODULE_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "module/"
    flask_app.config['UPLOAD_LOG_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "log/"
    flask_app.config['APP_LOG_FOLDER'] = "/root/CodingHub/logs/"
    flask_app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    flask_app.config.update(
        MONGO_HOST='localhost',
        MONGO_PORT=27017,
        # MONGO_USERNAME='zuiwan',
        # MONGO_PASSWORD='zuiwan',
        MONGO_DBNAME='CodingHub'
    )
    flask_app.config['REDIS_HOST'] = HOST
    flask_app.config['REDIS_PORT'] = 6380
    flask_app.config['REDIS_DB'] = 0
    flask_app.config.update(
        CELERY_BROKER_URL='redis://{}:{}'.format(RedisHost, RedisPort),
        CELERY_RESULT_BACKEND='redis://{}:{}'.format(RedisHost, RedisPort),
    )
    flask_app.secret_key = 'i-like-python-nmba'
    return flask_app


flask_app = create_app()
