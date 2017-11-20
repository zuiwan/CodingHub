from sqlalchemy import and_

from Library.extensions import orm
from Library.OrmModel.User import User
from Library.OrmModel.Farovite import Favorite

class FavoriteDBM():
    def __init__(self):
        pass
    def add(self, data):
        # data = {'url': 'url'}
        fav = Favorite(**data)
        # fav = Favorite(owner_id='')
        orm.session.add(fav)
        orm.session.commit()

    def query(self, data):
        sql = Favorite.query.filter(
            and_(
                Favorite.id == data.get('id'),
                Favorite.name == data.get('name')
            )
        )
        records = sql.all()
        Favorite.query.filter_by(id=data.get('id')).first()

    def delete(self,url,project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.url == url,
                Favorite.project_id == project_id
            )
        )
        record = sql.first()
        orm.session.delete(record)
        orm.session.commit()

    def query_by_project(self,project_id):
        sql=Favorite.query.filter(Favorite.project_id==project_id)
        records=sql.all()
        return records

    def query_by_tags(self,tags):
        sql=Favorite.query.filter(Favorite.tags==tags)
        records=sql.all()
        return records
    
    # def get_unread_list(self):
    #     sql = Favorite.query.filter(Favorite.is_unread == False)
    #     records = sql.all()
    #     return records

    def modify(self):
        return 0

    def Is_Url_Existed(self, url, project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.url ==  url,
                Favorite.project_id == project_id
            )
        )
        records = sql.all()
        return records


