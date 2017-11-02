# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
from flask import g, jsonify, Response, stream_with_context, render_template, send_file, Response

from Library import error_util as ED
class User_API(Resource):
    def get(self):
        return {'code': 200, 'data': 'hello world'}