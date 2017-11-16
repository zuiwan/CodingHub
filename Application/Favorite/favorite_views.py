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
        '''
        login
        :return:
        '''

        # type = {0: 'test', 1: 'default'}
        # result = {'code': ED.no_err}
        # result['data'] = {'uid': str(g.user.id),
        #                   'username': g.user.username,
        #
        #                   'email': g.user.email,
        #                   }

        fc = FavoriteCenter()
        result = fc.add(json.loads(request.data))
        return result
