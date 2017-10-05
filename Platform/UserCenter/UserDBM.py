#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import json

from Libraries.Singleton.Singleton import Singleton
import datetime
import time
import ErrorDefine as ED

from Utils import *
from Libraries.DBModel import *
from ConfigCenter.ConfigCenter import ConfigCenter
from LogCenter.LogCenter import LogCenter

from UserCenter.UserDBManager import UserDBManager
from UserAddressCenter.UserAddressDBManager import UserAddressDBManager


@Singleton
class UserDBM():
    def __init__(self):
        self.logger = LogCenter.instance().get_logger('CerCenterLog')
        self.conf = ConfigCenter.instance().get_parser('CerCenter')
        self.db_model = DBModelFactory.instance().get_db_model()
        self.db_model_read = DBModelFactory.instance().get_db_model(readonly=True)

        self.table_name = self.conf.get('RDS', 'table_name')
        self.table_name_count = self.conf.getint('RDS', 'table_name_count')
        self.table_name_keys = json.loads(self.conf.get('RDS', 'table_name_keys'))

        self.table_name_pay_order = ConfigCenter.instance().get_parser('OrderCenter').get('RDS', 'table_name_order')

        self.userDBManager = UserDBManager.instance()
        self.userAddressDBManager = UserAddressDBManager.instance()