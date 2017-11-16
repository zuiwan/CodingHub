#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import g, jsonify
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from Library import error_util as ED
from Library.OrmModel.User import User,SECRET_KEY
from Library.extensions import orm

import traceback

from flask import request, g
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import or_, and_, extract
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.datastructures import Authorization

from Library.extensions import orm
from Library.OrmModel.User import User

class User_Center(object):
    http_basic_auth=HTTPBasicAuth()

    def __init__(self,owner_id):
        self.owner_id=owner_id

    @staticmethod
    def Is_User_Existed(user_id_or_name):
        flag = False
        if User.query.filter(and_(or_(
                        User.id == user_id_or_name,
                        User.username == user_id_or_name,
                        User.email == user_id_or_name),
                        User.is_deleted == 0)).first():
            flag = True
        return flag

    @staticmethod
    def Is_Email_Existed(email):
        if User.query.filter_by(email=email).first():
            return True
        else:
            return False

    @staticmethod
    def Get_User(**find_by):
        _id = find_by.get('id') or find_by.get('user_id')
        _name = find_by.get('name') or find_by.get('user_name') or find_by.get('username')
        _email = find_by.get('email')
        return User.query.filter(and_(or_(User.id == _id,
                                          User.username == _name,
                                          User.email == _email),
                                      User.is_deleted == 0)).first()

    @staticmethod
    def Update_User_Setting(id, username=None, email=None, password=None):
        user = User.query.get(id)
        if user:
            if username is not None:
                user.username = username
            if password is not None:
                user.hash_password(password)
            if email is not None:
                user.email = email

            orm.session.commit()
            return user
        else:
            return None

http_basic_auth = User_Center.http_basic_auth
@ED.auth_error_handler(http_basic_auth)
def Unauthorized_Handler():
    return jsonify(ED.Respond_Err(ED.err_no_auth, "账号或密码错误，请重试"))

@http_basic_auth.verify_password
def Verify_Password(username_or_token, password):
    # user_controler_logger.info('@'.join((str(username_or_token), str(password))))
    # first try to authenticate by token
    user = Verify_Auth_Token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User_Center.Get_User(username=username_or_token)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

def Verify_Auth_Token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    user = User.query.get(data['id'])
    return user



def Regist_With_Code(username, password, email):
    if username is None or password is None or User.query.filter_by(username=username).first() is not None:
        return False

    # code_object = InvitedCode.query.filter_by(code=invite_code, user_id=None).first()
    # if code_object is None:
    #     return None
    #
    # if code_object.is_vip == 0:
    #     type = 1
    # else:
    #     type = 0
    user = User(username=username, email=email)
    user.hash_password(password)
    orm.session.add(user)
    orm.session.commit()

    # code_object.user_id = user.id
    # db.session.commit()
    #
    # user_profile = Create_User_Profile(user.id, user.username)
    # if user.type == 0:
    #     default_balance = VIP_GIFT_MONEY
    #     user_controler_logger.info("VIP用户赠送100元余额，充值成功")
    # else:
    #     default_balance = 0
    # account = Account_Center.Create_Account(owner_id=user.id, balance=default_balance)
    # if not account:
    #     user_controler_logger.error("Account表插入失败，注册失败")
    #     return False
    return user

