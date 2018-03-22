#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys

sys.path.append("..")
sys.path.append(".")
from Library.extensions import orm

from Library.OrmModel.User import User
from Library.OrmModel.Project import Project
from Library.OrmModel.Farovite import Favorite
from Library.OrmModel.Contacts import Contacts
from Library.OrmModel.UserProfile import UserProfile
from Library.OrmModel.Product import Product

orm.create_all()
