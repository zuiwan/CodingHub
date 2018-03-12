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

from flask_restful import Resource, reqparse
import flask
from Platform.UserCenter.UserCenter import (
    UserCenter_Ist,
    LoginCenter_Ist,
    RegistCenter_Ist
)
from Platform.UserCenter.UserControler import (
    UserController
)
from Library.Utils.net_util import (
    package_json_request_data,
)

from Library import ErrorDefine as ED

class ContactsAPI(Resource):
    '''
    购物车相关的批量操作
    '''
    url = "/api/v1/contacts/<string:namespace>"
    endpoint = "user-shopping-cart-api"

    # @LoginCenter_Ist.http_basic_auth.login_required
    def get(self, namespace):
        '''
        获取购物车列表
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        parser = reqparse.RequestParser()
        parser.add_argument("token", type=str, location="args")
        parser.add_argument("query_name", type=str, location="args")
        parser.add_argument("query_nickname", type=str, location="args")
        args = parser.parse_args()

        uc = UserController(flask.g.user)
        result["data"] = uc.sc.find_shopping_carts()

        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def put(self, name):
        '''
        批量添加商品到购物车
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        uc = UserController(flask.g.user)
        uc.add_many_to_shopping_cart(data["products"])
        return result

    def post(self, name):
        '''
        批量修改购物车设置
        :return:
        '''
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        # TODO
        parser = reqparse.RequestParser()
        parser.add_argument('', type=int, location='args')
        args = parser.parse_args()
        return result

    @LoginCenter_Ist.http_basic_auth.login_required
    def delete(self, name):
        result = ED.Respond_Err(ED.no_err)
        uc = UserController(flask.g.user)
        uc.sc.clear_shopping_carts()
        return result

class UserShoppingCartItemAPI(Resource):
    url = "/api/v1/user/<string:name>/shopping_cart/<string:product_id>"
    endpoint = "user-shopping-cart-item-api"

    @LoginCenter_Ist.http_basic_auth.login_required
    @package_json_request_data
    def put(self, name, product_id):
        result = ED.Respond_Err(ED.no_err)
        data = flask.request.data
        uc = UserController(flask.g.user)
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
        data = flask.request.data
        uc = UserController(flask.g.user)
        uc.sc.update_item(product_id, data[product_id])
        return result
