#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     exceptions
   Description :
   Author :       huangzhen
   date：          2018/1/2
-------------------------------------------------
   Change Activity:
                   2018/1/2:
-------------------------------------------------
"""
__author__ = 'huangzhen'

class RussellException(Exception):

    def __init__(self, message=None, code=None):
        super(RussellException, self).__init__(message)

class NotFoundException(Exception):

    def __init__(self, message="The resource you are looking for is not found. Check if the id is correct."):
        super(NotFoundException, self).__init__(message)

class OverLimitException(Exception):

    def __init__(self, message="You are over the allowed limits for this operation. Consider upgrading your account."):
        super(OverLimitException, self).__init__(message)

class ServiceBusyException(Exception):
    def __init__(self,
                 message="Service is busy right now. "):
        super(ServiceBusyException, self).__init__(message)

class ServiceUnavailableException(Exception):
    def __init__(self,
                 message="Infrastructure Cloud Service is unavailable right now."):
        super(ServiceUnavailableException, self).__init__(message)

class ResourceUnavailableException(Exception):
    def __init__(self,
                 message="The resource is unavailable right now. Please retry after a while or contact the development team via contact@russellcloud.cn"):
        super(ResourceUnavailableException, self).__init__(message)