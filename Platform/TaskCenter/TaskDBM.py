#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from Library.singleton import Singleton
import datetime
import time
import Library.ErrorDefine as _ED

from Library.Utils import *
from Library.db_model import *

from Platform.UserCenter.UserDBM import UserDBM


@Singleton
class TaskDBM():
    from Library.OrmModel.Task import Task
    from Library.OrmModel.Project import Project
    from Library.OrmModel.TaskInstance import TaskInstance
    def __init__(self):
        self.logger = LogCenter.instance().get_logger('CerCenterLog')
        self.db_model = DBModelFactory.instance().get_db_model()
        self.db_model_read = DBModelFactory.instance().get_db_model(readonly=True)

        # self.table_name = self.conf.get('RDS', 'table_name')
        self.table_name = "task"
        # self.table_name_count = self.conf.getint('RDS', 'table_name_count')
        # self.table_name_keys = json.loads(self.conf.get('RDS', 'table_name_keys'))
        self.table_keys = ()
        # self.table_name_pay_order = ConfigCenter.instance().get_parser('OrderCenter').get('RDS', 'table_name_order')

        self.userDBM = UserDBM.instance()

    def insert_task(self):
        pass

    def insert_task_instance(self):
        pass

