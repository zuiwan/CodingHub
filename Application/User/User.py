# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
from flask import (
    render_template,
    request,
    g,
    Blueprint
)
from Application.utils import (
    G_Folder,
    G_App_Folder
)
from Platform.UserCenter.UserCenter import (
    UserCenter_Ist,
    LoginCenter_Ist,
    RegistCenter_Ist,
)
from Platform.UserCenter.UserControler import (
    UserController
)
from Library.Utils.net_util import (
    package_json_request_data,
    auth_field_in_data
)

from Library import ErrorDefine as ED

UserView = Blueprint("UserView", __name__, template_folder="{}/User/templates".format(G_App_Folder),
                     static_folder="{}/static/User/static".format(G_Folder))


@UserView.route("UserView/register", methods=["GET"])
def registerView():
    return render_template("register.html")

@UserView.route("UserView/login", methods=["GET"])
def loginView():
    return render_template("login.html")


class User_API(Resource):
    url = "/api/v1/user"
    endpoint = "user-api"

    # @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    @auth_field_in_data("name")
    def get(self):
        '''
        login
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = request.data

        if LoginCenter_Ist.Is_User_Logined() and data["name"] == g.user.name:
            result["data"] = g.user.to_dict()
        else:
            tu = UserCenter_Ist.Get_User(name=data["name"])
            uc = UserController(tu)
            result["data"] = uc.profile

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def put(self):
        '''
        update info of existed user
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = request.data
        user = UserController(UserCenter_Ist.Get_User(name=g.user.name))
        user.update(data)
        return result

    @auth_field_in_data("name", "password", "phone")
    @package_json_request_data
    def post(self):
        '''
        注册
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = request.data
        result["data"] = RegistCenter_Ist.Regist(data["name"],
                                                 data["password"],
                                                 data["phone"])
        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def delete(self):
        result = ED.Respond_Err(ED.no_err)
        g.user.delete()
        return result
