#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from marshmallow import Schema, fields, post_load
from Library.extensions import orm
import datetime

class BaseSchema(Schema):
    __abstract__  = True
    id = fields.Str()
    date_created = fields.DateTime(allow_none=True)
    date_modified = fields.DateTime(allow_none=True)
    is_deleted = fields.Boolean()

class BaseModel(orm.Model):
    """
    Base for all model classes
    """
    __abstract__  = True

    id = orm.Column(orm.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    date_created = orm.Column(orm.DateTime, default=lambda:datetime.datetime.utcnow())
    date_modified = orm.Column(orm.DateTime, default=lambda:datetime.datetime.utcnow(), onupdate=lambda:datetime.datetime.utcnow())
    is_deleted =  orm.Column(orm.Integer, default=False)


    def to_dict(self):
        return self.schema.dump(self).data

    def delete(self):
        self.is_deleted = 1
        orm.session.commit()
        return True

    @classmethod
    def from_dict(cls, dct):
        return cls.schema.load(dct).data
