#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       ContactsControler
   Description:
   Author:          huangzhen
   date:            2018/3/22
-------------------------------------------------
   Change Activity:
                   2018/3/22:
-------------------------------------------------
"""

__author__ = 'huangzhen'
from sqlalchemy import and_
from sqlalchemy import distinct
from Library.OrmModel.Contacts import Contacts
from Library.OrmModel.User import User
from Library.extensions import orm
from .UserCenter import RegistCenter_Ist


class ContactsControler(object):
    def __init__(self, namespaces, user_id=None):
        if isinstance(namespaces, str) or isinstance(namespaces, basestring):
            namespaces = (namespaces,)
        assert isinstance(namespaces, tuple)
        if "all" in namespaces:
            namespaces = orm.session.query(distinct(Contacts.namespace)).all()
        self.namespaces = namespaces
        self.user_id = user_id
        self.db = orm

    def Get_All(self):
        _r = {}
        _n = 0
        for ns in self.namespaces:
            if ns not in _r:
                _r[ns] = []
            a, b = self.Get_Namespace(ns)
            _r[ns].append(a)
            _n += b
        return _r, _n

    def Get_Namespace(self, ns):
        q = Contacts.query.filter(and_(
            Contacts.is_deleted == 0,
            Contacts.namespace == ns))
        try:
            _r = q.all()
            _n = q.count()
        except Exception as e:
            _r, _n = [], 0
        return _r, _n

    def Create(self, info):
        try:
            uid = RegistCenter_Ist.Regist_And_Return_Id(name=info["name"],
                                                        phone=info["phone"],
                                                        password=info.get("password", "666666"))
        except ValueError as e:
            uid = str(e).split(' ')[0]
        c = Contacts(namespace=info["namespace"],
                     owner_id=uid,
                     nickname=info.get("nickname"),
                     org=info.get("org"),
                     addresses=info["addresses"],
                     phone=info["phone"],
                     city=info["city"],
                     source_ip=info["ip"],
                     name=info["name"])
        self.db.session.add(c)
        return True
