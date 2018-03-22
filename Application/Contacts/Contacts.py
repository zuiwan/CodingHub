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
    # html_text = Environment(loader=BaseLoader).from_string(
    #     Get_Template("Contacts/index.html").decode("utf-8")).render(
    #     contacts_info=contacts_info
    # )
    # return html_text[
    #     [{
    #       name:'banana',
    #       badge: 'http://www.freeiconspng.com/uploads/pikachu-png-icon-7.png'
    #     },]
    return render_template("index.html")


class ContactsAPI(Resource):
    '''
    购物车相关的批量操作
    '''
    url = "/api/v1/contacts/<string:namespace>"
    endpoint = "contacts-api"
    decorators = [auth_field_in_data(token=str("SECRET_KEY")),
                  package_json_request_data,
                  check_api_cost_time]

    def get(self, namespace):
        '''
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        # parser.add_argument("token", type=str, location="args")
        # parser.add_argument("query_name", type=str, location="args")
        # parser.add_argument("query_nickname", type=str, location="args")

        # uc = UserController(T_G.user)

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
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

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def delete(self, name):
        result = ED.Respond_Err(ED.no_err)
        uc = UserController(T_G.user)
        uc.sc.clear_shopping_carts()
        return result


class UserShoppingCartItemAPI(Resource):
    url = "/api/v1/user/<string:name>/shopping_cart/<string:product_id>"
    endpoint = "user-shopping-cart-item-api"

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def put(self, name, product_id):
        result = ED.Respond_Err(ED.no_err)
        data = request.data
        uc = UserController(T_G.user)
        uc.add_one_to_shopping_cart(product_id=product_id,
                                    unit_price=data["unit_price"],
                                    count=data["count"],
                                    address=data["address"])
        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def post(self, name, product_id):
        '''
        修改购物车中商品（商品数量，收货地址等）
        :param name:
        :param product_id:
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = request.data
        uc = UserController(T_G.user)
        uc.sc.update_item(product_id, data[product_id])
        return result
