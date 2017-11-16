#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import jsonify
from flask_restful import Api
from Application.app import flask_app

api = Api(flask_app)
from Application.User.user_views import User_API
from Application.Favorite.favorite_views import Favorite_API

api.add_resource(User_API, '/api/v1/user', endpoint='user')
api.add_resource(Favorite_API, '/api/v1/favorite', endpoint="favorite")
@flask_app.route('/', methods=['GET'])
def index():
    return jsonify(dict(message="Hello World"))


@flask_app.route('/api/v1/db/demo', methods=['GET'])
def dbdemo():
    from Library.db_model import DBModelFactory, DBModel
    from Library.extensions import orm
    from Library.OrmModel.User import User
    db_model = DBModelFactory.instance().get_db_model()
    users = User.query.all()
    new_list = []
    for user in users:
        new_list.append(user.to_dict())

    select_sql = DBModel.sql_select('user',
                                    keys=['id', 'date_created', 'username'],
                                    where=DBModel.sql_and({}),
                                    limit='0,%d' % 5, order=[{'key': 'date_created', 'desc': True}])
    records = db_model.GetList(select_sql, options={"table_count": 1})

    return jsonify({'orm': new_list, 'sql': records})