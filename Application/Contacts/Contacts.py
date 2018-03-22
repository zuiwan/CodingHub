#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       Contacts
   Description:
   Author:          huangzhen
   date:            2018/3/13
-------------------------------------------------
   Change Activity:
                   2018/3/13:
-------------------------------------------------
"""
from Platform.UserCenter.ContactsControler import ContactsControler

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
from jinja2 import Environment, BaseLoader

ContactsView = Blueprint("Contacts", __name__, template_folder="{}/Contacts/templates".format(G_App_Folder),
                         static_folder="{}/static/Contacts/static".format(G_Folder))


@ContactsView.route("ContactsView/<string:namespace>", methods=["GET"])
def contactsView(namespace):
    contacts_info = {}
    # return html_text[
    #     [{
    #       name:'banana',
    #       badge: 'http://www.freeiconspng.com/uploads/pikachu-png-icon-7.png'
    #     },]
    return render_template("index.html", namespace=namespace)


@ContactsView.route("ContactsView/registerView", methods=["GET"])
def contactsRegisterView():
    return render_template("register.html")


class ContactsAPI(Resource):
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
        _ls = cc.Get_All()
        for l in _ls:
            l = l.to_dict()
            l.update({"badge": 'http://www.freeiconspng.com/uploads/pikachu-png-icon-7.png'})
        result["data"] = _ls

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def put(self, namespace):
        '''
        修改
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = request.data
        uc = UserController(T_G.user)
        uc.add_many_to_shopping_cart(data["products"])
        return result

    def post(self, namespace):
        '''
        新增
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = request.data
        cc = ContactsControler(namespace)
        if data.get("address2"):
            data["addresses"] = data["address"] + ',' + data["address2"]
        if not cc.Create(data):
            return ED.Respond_Err(ED.unknown_err)
        result["data"] = namespace
        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def delete(self, name):
        result = ED.Respond_Err(ED.no_err)
        uc = UserController(T_G.user)
        uc.sc.clear_shopping_carts()
        return result
