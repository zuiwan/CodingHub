#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask

flask_app = Flask(__name__,static_url_path='/assets', static_folder='assets', template_folder='templates')

# import api

# initialization
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://zuiwan:zuiwan@localhost:3306/zuiwan'
flask_app.config['KAFKA_BROKER_URI'] = ['']

flask_app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
flask_app.config['UPLOAD_WORK_FOLDER'] = "/root/workspace/"
flask_app.config['UPLOAD_DATA_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "data/"
flask_app.config['UPLOAD_EXPERIMENT_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "experiment/"
flask_app.config['UPLOAD_MODULE_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "module/"
flask_app.config['UPLOAD_LOG_FOLDER'] = flask_app.config['UPLOAD_WORK_FOLDER'] + "log/"
flask_app.config['APP_LOG_FOLDER'] = "/root/CodingLife_Server/logs/"
flask_app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
# flask_app.config['SQLALCHEMY_ECHO'] = True

#
# flask_app.config['latest_version'] = '0.3.2'
# flask_app.config['min_version'] = '0.3.2'
flask_app.config['ALLOWED_EXTENSIONS'] = set(['py'])

flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
)
flask_app.secret_key = 'i-like-python-nmba'



