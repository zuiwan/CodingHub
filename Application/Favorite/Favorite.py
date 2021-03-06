# -*- coding:utf-8 -*-
import traceback
from flask_restful import Resource, reqparse
from flask import request, g, jsonify, Response, stream_with_context, render_template, send_file, Response

from Library.Utils.log_util import (
    LogCenter,
)
from Library import ErrorDefine as _ED

from Platform.FavoriteCenter.FavoriteCenter import FavoriteCenter
from Platform.UserCenter.UserCenter import (
    UserCenter_Ist as UC_IST,
    LoginCenter_Ist as LC_IST
)

import json

FC_IST = FavoriteCenter.instance()
favorite_view_logger = LogCenter.instance().get_logger("view", "favorite")

http_basic_auth = LC_IST.http_basic_auth


class Favorite_API(Resource):
    @http_basic_auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("project_id", type=int, location="args")
        parser.add_argument("tag", type=str, location="args")
        parser.add_argument("name", type=str, location="args")
        parser.add_argument("catalog", type=str, location="args")
        parser.add_argument("is_unread", type=bool, location="args")
        parser.add_argument("is_recommended", type=bool, location="args")
        args = parser.parse_args()
        result = _ED.Respond_Err(_ED.no_err)
        ### TODO
        ### err_code, out_data = FC_IST.Get_Favorites(data)

        if args["project_id"]:
            err_code, out_data = FC_IST.Query_Favorite_By_ProjectId(args["project_id"])
            if not err_code == _ED.no_err:
                return _ED.Respond_Err(_ED.no_err)
        elif args["tags"]:
            err_code, out_data = FC_IST.Query_Favorite_By_Tags(args["tags"])
            if not err_code == _ED.no_err:
                return _ED.Respond_Err(_ED.no_err)
        else:
            err_code, out_data = _ED.err_req_data, None

        if not err_code == _ED.no_err:
            return _ED.Respond_Err(_ED.no_err)
        result['data'] = out_data
        return result

    @http_basic_auth.login_required
    def post(self):
        try:
            data = json.loads(request.data)
        except Exception as e:
            favorite_view_logger.error(traceback.format_exc())
            return _ED.Respond_Err(_ED.err_req_data)
        result = _ED.Respond_Err(_ED.no_err)
        action = data.get('action')
        if action == "create":
            err_code, out_data = FC_IST.Create_Favorite(data)
        else:
            err_code, out_data = FC_IST.Update_Favorite(data)

        if not err_code == _ED.no_err:
            return _ED.Respond_Err(_ED.no_err)
        result['data'] = out_data
        return result

    @http_basic_auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=str, location="args")
        args = parser.parse_args()
        result = _ED.Respond_Err(_ED.no_err)
        err_code, out_data = FC_IST.Delete_Favorite(args)

        if not err_code == _ED.no_err:
            return _ED.Respond_Err(_ED.no_err)
        result['data'] = out_data
        return result
