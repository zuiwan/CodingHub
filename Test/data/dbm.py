from Library.extensions import orm, flask_app


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


migrate = Migrate(flask_app, orm)

manager = Manager(flask_app)
manager.add_command('db', MigrateCommand)

from Library.OrmModel.user import User
from Library.OrmModel.profile import UserProfile
from Library.OrmModel.Project import Project

from flask_sqlalchemy import SQLAlchemy

manager.run()