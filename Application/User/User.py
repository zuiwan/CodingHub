# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
import flask
from Platform.UserCenter.UserCenter import (
    UserCenter_Ist,
    LoginCenter_Ist,
    RegistCenter_Ist
)
from Library.Utils.net_util import (
    package_json_request_data,
    require_field_in_data
)

from Library import ErrorDefine as ED


class User_API(Resource):
    url = "/api/v1/user"
    endpoint = "user-api"

    # @LoginCenter_Ist.http_basic_auth.login_required
    @require_field_in_data("name")
    @package_json_request_data
    def get(self):
        '''
        login
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data

        if UserCenter_Ist.Is_User_Logined() and data["name"] == flask.g.user.name:
            result["data"] = flask.g.user.to_dict()
        else:
            tu = UserCenter_Ist.Get_User(name=data["name"])
            result["data"] = tu.profile

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def put(self):
        '''
        update info of existed user
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        user = UserCenter_Ist.Get_User(name=flask.g.user.name)
        user.update(data)
        return result

    @require_field_in_data("name", "password", "email")
    @package_json_request_data
    def post(self):
        '''
        注册
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        result["data"] = RegistCenter_Ist.Regist(data["name"],
                                                 data["password"],
                                                 data["email"])
        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def delete(self):
        result = ED.Respond_Err(ED.no_err)
        flask.g.user.delete()
        return result
