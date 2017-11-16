#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       MallCenter
   Description:
   Author:          huangzhen
   date:            2018/3/4
-------------------------------------------------
   Change Activity:
                   2018/3/4:
-------------------------------------------------
"""
__author__ = 'huangzhen'

import flask
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from Library import ErrorDefine as ED
from Library.OrmModel.User import User, SECRET_KEY
from Library.extensions import orm
from Library.Utils.log_util import LogCenter
import traceback

from sqlalchemy import or_, and_, extract
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.datastructures import Authorization

from Library.extensions import orm
from Library.OrmModel.User import User
from Library.OrmModel.ShoppingCart import ShoppingCart
from Library.OrmModel.UserProfile import UserProfile
from Library.singleton import Singleton


@Singleton
class MallCenter(object):
    def __init__(self):
        self.db = orm
        self.logger = LogCenter.instance().get_logger("MallCenter", "mall-center")


@Singleton
class ShoppingCartCenter(object):
    def __init__(self):
        self.db = orm
        self.logger = LogCenter.instance().get_logger("MallCenter", "shopping-cart-center")



MallCenter_Ist = MallCenter.instance()
ShoppingCart_Ist = ShoppingCartCenter.instance()