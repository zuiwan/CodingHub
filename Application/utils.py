#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       utils
   Description:
   Author:          huangzhen
   date:            2018/3/22
-------------------------------------------------
   Change Activity:
                   2018/3/22:
-------------------------------------------------
"""
__author__ = 'huangzhen'

def Get_Template(template):
    with open('Application/templates/{}'.format(template), 'r') as f:
        content = f.read()
    return content
G_Folder = "/root/CodingHub"
G_App_Folder = G_Folder + "/Application"
