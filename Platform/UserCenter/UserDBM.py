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
from Library.Utils.log_util import LogCenter
from Library.OrmModel.Contacts import Contacts
from Library.extensions import orm


@Singleton
class UserDBM(object):
    def __init__(self):
        self.db = orm
        self.logger = LogCenter.instance().get_logger('UserCenterLog')
        # self.db_model = DBModelFactory.instance().get_db_model()
        # self.db_model_read = DBModelFactory.instance().get_db_model(readonly=True)
        #
        # self.table_name = self.conf.get('RDS', 'table_name')
        # self.table_name_count = self.conf.getint('RDS', 'table_name_count')
        # self.table_name_keys = json.loads(self.conf.get('RDS', 'table_name_keys'))

    def Add_Contact(self, info):
        c = Contacts(namespace=info["namespace"],
                     owner_id=info["owner_id"],
                     nickname=info["nickname"],
                     org=info["org"],
                     phone=info["phone"],
                     city=info["city"],
                     addresses=info["addresses"])
        self.db.session.add(c)
        self.db.session.commit()
        return True
