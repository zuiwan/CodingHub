#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import json

from Library.singleton import Singleton
from Library import ErrorDefine as ED
from Library.db_model import (
    DBModel,
    DBModelFactory
)
from Library.Utils import LogCenter


@Singleton
class UserDBM(object):
    def __init__(self):
        self.logger = LogCenter.instance().get_logger('UserCenterLog')
        self.db_model = DBModelFactory.instance().get_db_model()
        self.db_model_read = DBModelFactory.instance().get_db_model(readonly=True)

        self.table_name = self.conf.get('RDS', 'table_name')
        self.table_name_count = self.conf.getint('RDS', 'table_name_count')
        self.table_name_keys = json.loads(self.conf.get('RDS', 'table_name_keys'))
