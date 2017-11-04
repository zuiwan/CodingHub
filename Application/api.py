#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import jsonify
from flask_restful import Api
from Application.app import flask_app

api = Api(flask_app)
from Application.User.user_views import User_API

api.add_resource(User_API, '/api/v1/user', endpoint='user')

@flask_app.route('/', methods=['GET'])
def index():
    return jsonify(dict(message="Hello World"))