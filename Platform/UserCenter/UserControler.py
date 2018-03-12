#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       UserControler
   Description:
   Author:          huangzhen
   date:            2018/3/4
-------------------------------------------------
   Change Activity:
                   2018/3/4:
http://blog.51cto.com/jzfjeff/999314
-------------------------------------------------
"""
__author__ = 'huangzhen'
from sqlalchemy import or_, and_, extract
from Library.OrmModel.User import User
from Library.OrmModel.UserProfile import UserProfile
from .ShoppingCart import ShoppingCart, Item
from Library.extensions import orm, mongo
from .UserDBM import UserDBM


class UserController(object):
    def __init__(self, user):
        if not isinstance(user, User):
            raise NotImplementedError
        self.user = user
        self.userDBManager = UserDBM.instance()

    @property
    def owner_id(self):
        if getattr(self, "_owner_id", None) is None:
            self._owner_id = self.user.id
        return self._owner_id

    @property
    def sc(self):
        if getattr(self, "_sc", None) is None:
            self._sc = ShoppingCart(self.owner_id)
        return self._sc

    def update(self, data):
        name = data.get("name")
        if name is not None:
            self.name = name
        email = data.get("email")
        if email is not None:
            self.email = email
        level = data.get("level")
        if level is not None:
            if self.user.verify_admin_temp_token(data.get("token")):
                # 检查是否有修改权限
                self.level = level
        orm.session.commit()

    @property
    def profile(self):
        if getattr(self, "_profile", None) is None:
            self.__profile = UserProfile.query.filter(and_(
                or_(
                    UserProfile.owner_id == self.owner_id
                ),
                UserProfile.is_deleted == 0)).first()
            if self.__profile:
                self._profile = self.__profile.to_dict()
                # del self._profile["id"]
        return self._profile

    def add_one_to_shopping_cart(self, product_id, count, address, unit_price):
        self.sc.add_one(Item(product_id,
                             count,
                             address,
                             unit_price
                             ))
        doc = self.sc.save()
        return doc

    def add_many_to_shopping_cart(self, products):
        '''
        :param products: [{"product_id": .., "count": .., "address": .., "unit_price": ..}]
        :return:
        '''
        self.sc.add_many([Item(product["product_id"],
                               product["count"],
                               product["address"],
                               product["unit_price"]) for product in products])
        doc = self.sc.save()
        return doc
