from Application.api import flask_app
from Library.extensions import orm

from Library.OrmModel.User import User
from Library.OrmModel.Project import Project
orm.create_all()