from Library.OrmModel.User import User
from Library.OrmModel.Project import Project
from Library.extensions import orm


def create_users():
    usernames = ('huang', 'zhen')
    for username in usernames:
        user = User(username)
        orm.session.add(user)
        print user.id
    orm.session.commit()

def create_projects():
    projectsnames = ('huang', 'zhen')
    user = User.query.first()
    for projectsname in projectsnames:
        project = Project(name=projectsname, owner_id=user.id if user else '')
        orm.session.add(project)
        print project.id

    orm.session.commit()

if __name__ == '__main__':
    create_users()
    create_projects()
