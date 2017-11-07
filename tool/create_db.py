#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.path.append("..")
sys.path.append(".")
from Application.api import flask_app
from Library.extensions import orm

from Library.OrmModel.User import User
from Library.OrmModel.Project import Project
orm.create_all()