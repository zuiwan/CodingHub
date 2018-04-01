#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     patch
   Description :
   Author :       huangzhen
   date：          2017/12/29
-------------------------------------------------
   Change Activity:
                   2017/12/29:
-------------------------------------------------
"""

__author__ = 'huangzhen'
import json
import httplib

from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient

def AcsClient_Patch():
    # cause of aliyun's bug: https://github.com/aliyun/aliyun-openapi-python-sdk/issues/53
    # DO SOME TRICKS to fix aliyun's bug
    def fixed_do_action_with_exception(self, acs_request):
        # set server response format as json, because thie function will
        # parse the response so which format doesn't matter
        acs_request.set_accept_format('JSON')
        status, headers, body = self._implementation_of_do_action(acs_request)
        request_id = None
        try:
            # actually update body to dict
            body = json.loads(body)
            if isinstance(body, dict):
                request_id = body.get('RequestId')
        except AttributeError or ValueError or TypeError:
            # in case the response body is not a json string, return the raw
            # data instead
            pass

        if status < httplib.OK or status >= httplib.MULTIPLE_CHOICES:
            server_error_code, server_error_message = self._parse_error_info_from_response_body(
                body)
            raise ServerException(
                server_error_code,
                server_error_message,
                http_status=status,
                request_id=request_id)
        # body should be json dict
        return body

    AcsClient.do_action_with_exception = fixed_do_action_with_exception


if __name__ == 'App.aliyun_docker.patch':
    AcsClient_Patch()


