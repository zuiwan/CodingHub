#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       DlTask
   Description:
   Author:          huangzhen
   date:            2018/4/1
-------------------------------------------------
   Change Activity:
                   2018/4/1:
-------------------------------------------------
"""
__author__ = 'huangzhen'

from flask import (
    render_template,
    request,
    Blueprint,
    g as T_G
)
from flask_restful import Resource, reqparse
from Platform.UserCenter.UserCenter import (
    UserCenter_Ist,
    LoginCenter_Ist,
    RegistCenter_Ist
)
from Application.utils import (
    Get_Template,
    G_App_Folder,
    G_Folder
)

from Platform.UserCenter.UserControler import (
    UserController
)
from Library.Utils.log_util import check_api_cost_time
from Library.Utils.net_util import (
    package_json_request_data,
    auth_field_in_data,
)
from Library import ErrorDefine as ED

DLTaskView = Blueprint("DLTask", __name__, template_folder="{}/DLTask/templates".format(G_App_Folder),
                       static_folder="{}/static/DLTask/static".format(G_Folder))


@DLTaskView.route("DLTaskView/<string:namespace>", methods=["GET"])
def contactsView(namespace):
    return render_template("index.html", namespace=namespace)

class JobSpecAPI(Resource):
    url = "/api/v1/job/specification/<string:id>"
    endpoint = "jobspec"
    decorators = [package_json_request_data,
                  check_api_cost_time]
    def get(self, id):
        pass

    def post(self, id):
        # 创建新的作业描述
        data = request.data


class JobSubmitAPI(Resource):
    '''
    购物车相关的批量操作
    '''
    url = "/api/v1/contacts/<string:namespace>"
    endpoint = "contacts-api"
    decorators = [package_json_request_data,
                  check_api_cost_time]

    def get(self, namespace):
        '''
        免登陆
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        cc = ContactsControler(namespace)
        _ls, _n = cc.Get_Namespace(namespace)
        res = []
        for l in _ls:
            l = l.to_dict()
            l.update({"badge": 'http://www.freeiconspng.com/uploads/pikachu-png-icon-7.png'})
            res.append(l)

        result["data"] = {"list": res, "num": _n}

        return result

