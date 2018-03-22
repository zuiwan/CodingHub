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
from sqlalchemy import and_

__author__ = 'huangzhen'

from Library.OrmModel.Contacts import Contacts


class ContactsControler(object):
    def __init__(self, namespaces, user_id):
        if isinstance(namespaces, str) or isinstance(namespaces, basestring):
            namespaces = (namespaces,)
        assert isinstance(namespaces, tuple)
        self.namespaces = namespaces
        self.user_id = user_id

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
