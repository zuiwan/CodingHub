# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
from flask import request, g, jsonify, Response, stream_with_context, render_template, send_file, Response

from Platform.FavoriteCenter.FavoriteCenter import FavoriteCenter
from Platform.UserCenter.UserCenter import User_Center

http_basic_auth = User_Center.http_basic_auth
from Library.data_util import *
from Library import error_util as ED
class Favorite_API(Resource):
    @http_basic_auth.login_required
    def post(self):
        return 0


    @http_basic_auth.login_required
    def get(self):
        return 0

    @http_basic_auth.login_required
    def put(self):
        fc = FavoriteCenter()
        result = fc.add(json.loads(request.data))
        return result

    @http_basic_auth.login_required
    def delete(self):
        fc=FavoriteCenter()
        result = fc.delete(json.loads(request.data))
        return result
