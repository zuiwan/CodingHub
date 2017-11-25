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
        parser=reqparse.RequestParser()
        parser.add_argument("project_id",type=int,location="args")
        parser.add_argument("tags",type=str,location="args")
        parser.add_argument("name",type=str,location="args")
        parser.add_argument("catalog",type=str,location="args")
        parser.add_argument("is_unread",type=bool,location="args")

        # parser.add_argument("is_unread", type=int, location="args")
        args=parser.parse_args()
        fc = FavoriteCenter()

        results=''
        if args["project_id"]:
            results = fc.Query_Favorite_By_ProjectId(args["project_id"])
        elif args["tags"]:
            results = fc.Query_Favorite_By_Tags(args["tags"])
        # elif args["is_unread"]:
        #     return "in_unread"

        return results

    @http_basic_auth.login_required
    def put(self):
        fc = FavoriteCenter()
        result = fc.Create_Favorite(json.loads(request.data))
        return result

    @http_basic_auth.login_required
    def delete(self):
        fc=FavoriteCenter()
        result = fc.Delete_Favorite(json.loads(request.data))
        return result
