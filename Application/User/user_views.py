# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
from flask import request, g, jsonify, Response, stream_with_context, render_template, send_file, Response
from Platform.UserCenter.UserCenter import Regist_With_Code, UserCenter

http_basic_auth = UserCenter.http_basic_auth
from Application.User.user_manager import *


from Library.data_util import *
from Library import error_util as ED
class User_API(Resource):
    @http_basic_auth.login_required
    def get(self):
        '''
        login
        :return:
        '''
        type = {0: 'test', 1: 'default'}
        result = {'code': ED.no_err}
        result['data'] = {'uid': str(g.user.id),
                          'username': g.user.username,

                          'email': g.user.email,
                          }
        return result

    def put(self):
        '''
                register, need geetest validation.
                :return:
                '''
        result = {'code': ED.no_err}
        if request.form:
            # check geetest
            # if not (request.form.get(gt.FN_VALIDATE) or request.form.get(gt.FN_CHALLENGE) or request.form.get(
            #        gt.FN_SECCODE)):
            #    return ED.Respond_Err(ED.err_req_data, '缺少极验验证')
            # status = session.get(gt.GT_STATUS_SESSION_KEY)
            # user_id = session.get("user_id_hashed")
            # if not Verify_Geetest(request.form, status, user_id):
            #    return ED.Respond_Err(ED.err_user_abnormal, '极验验证失败')

            # check username
            username = request.form.get('username')
            if not Is_Username_Validate(username):
                return ED.Respond_Err(ED.err_user_register_error, "用户名格式出错，只支持字母和符号")
            if UserCenter.Is_User_Existed(username):
                return ED.Respond_Err(ED.err_user_id_existed, "该名称已被使用")

            # check password
            password = request.form.get('password')
            if not Is_Password_Validate(password):
                return ED.Respond_Err(ED.err_password_format, "密码格式出错，必须包含字母和数字")

            # check email
            email = request.form.get('email')
            if not Is_Email_Validate(email):
                return ED.Respond_Err(ED.err_req_data, '邮箱格式出错')
            if UserCenter.Is_Email_Existed(email):
                return ED.Respond_Err(ED.err_user_id_existed, '该邮箱已注册')
            # check invite code
            # invite_code = request.form.get('code')
            # if not invite_code or len(invite_code) <= 0:
            #     return ED.Respond_Err(ED.err_user_register_error, '邀请码错误')
            # if not Check_Invited_Code(code=invite_code):
            #     return ED.Respond_Err(ED.err_code_invalid, '邀请码错误')

            # check verify code
            # verify_code = request.form.get('verify-code')
            # if not verify_code or len(verify_code) <= 0:
            #     return ED.Respond_Err(ED.err_user_register_error, '验证码错误')
            # if not Check_Verification_Code(verify_code, user_email=email):
            #     return ED.Respond_Err(ED.err_code_invalid, '验证码错误')

            # register
            user = Regist_With_Code(username, password, email)
            if user:
                result['data'] = {'username': user.username,
                                  'email': user.email}
            else:
                result = ED.Respond_Err(ED.err_user_register_error, "未知注册错误，请联系系统管理员")

        else:
            result = ED.Respond_Err(ED.err_no_req_data)
        return result

    @http_basic_auth.login_required
    def post(self):
        result = {'code': ED.no_err}
        if not request.form:
            return ED.Respond_Err(ED.err_no_req_data)
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user = UserCenter.Get_User(username=username)
        user = UserCenter.Update_User_Setting(id=user.id, username=username, email=email, password=password)
        if not user:
            return ED.Respond_Err(ED.err_sys)
        result['data'] = user.to_dict()
        return result

    @http_basic_auth.login_required
    def delete(self):
        result = {'code': ED.no_err}
        g.user.delete()
        return result