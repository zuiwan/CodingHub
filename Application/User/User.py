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
)

from Library import ErrorDefine as ED


class User_API(Resource):
    url = "/api/v1/user/<string:name>"
    endpoint = "user-api"

    # @LoginCenter_Ist.http_basic_auth.login_required
    def get(self, name):
        '''
        login
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        if UserCenter_Ist.Is_User_Logined() and name == flask.g.user.name:
            result["data"] = flask.g.user.to_dict()
        else:
            tu = UserCenter_Ist.Get_User(name=name)
            result["data"] = tu.profile

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def put(self, name):
        '''
        update info of existed user
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        user = UserCenter_Ist.Get_User(name=name)
        user.update(data)
        return result

    def post(self):
        '''
        注册
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        RegistCenter_Ist.Regist(data["name"],
                                data["password"],
                                data["email"])
        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def delete(self, name):
        result = ED.Respond_Err(ED.no_err)
        flask.g.user.delete()
        return result
