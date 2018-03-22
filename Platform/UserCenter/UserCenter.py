#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from Library import ErrorDefine as ED
from Library.OrmModel.User import User, SECRET_KEY
from Library.extensions import orm, mongo
from Library.Utils.log_util import LogCenter
import traceback

from sqlalchemy import or_, and_, extract
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.datastructures import Authorization

from Library.OrmModel.User import User
from .ShoppingCart import ShoppingCart
from Library.OrmModel.UserProfile import UserProfile
from Library.singleton import Singleton


@Singleton
class UserCenter(object):
    def __init__(self):
        self.db = orm
        self.logger = LogCenter.instance().get_logger("UserCenter", "regist-center")

    def Has_Permission(self, item, user=None):
        if getattr(item, "permission") <= 0:
            return True
        if isinstance(user, User) and item.owner_id == user.id:
            return True
        if self.Is_User_Logined():
            # logined and g hasattr user
            return item.owner_id == flask.g.user.id
        return False

    def Is_User_Existed(self, user_id_or_name):
        flag = False
        if User.query.filter(and_(or_(
                User.id == user_id_or_name,
                User.username == user_id_or_name,
                User.email == user_id_or_name),
                User.is_deleted == 0)).first():
            flag = True
        return flag

    def Is_Email_Existed(self, email):
        if User.query.filter_by(email=email).first():
            return True
        else:
            return False

    def Get_User(self, **find_by):
        _id = find_by.get('id') or find_by.get('user_id')
        _name = find_by.get('name') or find_by.get('user_name') or find_by.get('username')
        _email = find_by.get('email')
        return User.query.filter(and_(or_(User.id == _id,
                                          User.name == _name,
                                          User.email == _email),
                                      User.is_deleted == 0)).first()


@Singleton
class RegistCenter(object):
    def __init__(self):
        self.db = orm
        self.logger = LogCenter.instance().get_logger("UserCenter", "register-center")

    def Regist(self, name, password, phone, level=None):
        _ = self.Regist_And_Return_Id(name, password, phone, level)
        return True

    def Regist_And_Return_Id(self, name, password, phone, level=None):
        if name is None \
                or password is None \
                or User.query.filter_by(name=name).first() is not None:
            return False

        user = User(name=name, phone=phone, level=level)
        user.hash_password(password)
        self.db.session.add(user)
        self.db.session.flush()
        self.Fill_Tables(owner_id=user.id, phone=phone)
        # 提交事务
        self.db.session.commit()
        return user.id

    def Fill_Tables(self, owner_id, phone):
        self.db.session.add(UserProfile(owner_id=owner_id, phone=phone))
        ShoppingCart(owner_id).save()


#####################    ####################
RegistCenter_Ist = RegistCenter.instance()
UserCenter_Ist = UserCenter.instance()


@Singleton
class LoginCenter(object):
    http_basic_auth = HTTPBasicAuth()

    def __init__(self):
        self.http_basic_auth.verify_password(self.Verify_Password_Callback)
        self.db = orm
        self.logger = LogCenter.instance().get_logger("UserCenter", "login-center")

    #####################    ####################
    def Verify_Password_Callback(self, username_or_token, password):
        # TODO: 区分登录失败的不同情况
        self.logger.info("username:" + str(username_or_token))
        self.logger.info("password:" + str(password))
        if password is None:
            user = self.Verify_Auth_Token(username_or_token)
            if user:
                # token校验成功，提前返回
                return True
            else:
                # token校验失败
                return False
        # try to authenticate with username/password
        user = UserCenter_Ist.Get_User(name=username_or_token)
        if not user:
            return False
        if not user.verify_password(password):
            return False
        flask.g.user = user
        return True

    def Verify_Auth_Token(self, token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            # raise Exception("BadSignature")  # invalid token
            return None
        user = User.query.get(data['id'])
        return user

    def Is_User_Logined(self):
        request = flask.request
        if isinstance(getattr(flask.g, 'user', None), User):
            return True

        flask_auth = request.authorization
        if flask_auth is None and 'Authorization' in request.headers:
            # Flask/Werkzeug do not recognize any authentication types
            # other than Basic or Digest, so here we parse the header by
            # hand
            try:
                auth_type, token = flask.request.headers['Authorization'].split(
                    None, 1)
                flask_auth = Authorization(auth_type, {'token': token})
            except ValueError:
                # The Authorization header is either empty or has no token
                pass
        if flask_auth and flask_auth.username:
            password = self.http_basic_auth.get_password_callback(flask_auth.username)
        else:
            password = None
        if not self.http_basic_auth.authenticate(flask_auth, password):
            # Clear TCP receive buffer of any pending data
            request.data
            return False
        else:
            return True


LoginCenter_Ist = LoginCenter.instance()


@ED.auth_error_handler(LoginCenter_Ist.http_basic_auth)
def Unauthorized_Handler():
    return flask.jsonify(ED.Respond_Err(ED.err_user_login_expired, "登录过期，请重新登录"))
