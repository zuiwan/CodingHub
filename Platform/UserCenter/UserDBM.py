#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import json

from Library.singleton import Singleton
import Library.error_util as ED

from Library.db_model import *
from Library.log_util import LogCenter


@Singleton
class UserDBM():
    def __init__(self):
        self.logger = LogCenter.instance().get_logger('UserCenterLog')
        self.db_model = DBModelFactory.instance().get_db_model()
        self.db_model_read = DBModelFactory.instance().get_db_model(readonly=True)

        self.table_name = self.conf.get('RDS', 'table_name')
        self.table_name_count = self.conf.getint('RDS', 'table_name_count')
        self.table_name_keys = json.loads(self.conf.get('RDS', 'table_name_keys'))

        # self.table_name_pay_order = ConfigCenter.instance().get_parser('OrderCenter').get('RDS', 'table_name_order')

        self.userDBManager = UserDBManager.instance()