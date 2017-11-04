from Application.api import flask_app
from Library.extensions import orm

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


migrate = Migrate(flask_app, orm)

manager = Manager(flask_app)
manager.add_command('orm', MigrateCommand)

from Library.OrmModel.User import User
from Library.OrmModel.Project import Project

from flask_sqlalchemy import SQLAlchemy

manager.run()