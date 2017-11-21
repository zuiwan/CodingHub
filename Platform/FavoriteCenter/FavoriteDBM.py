from sqlalchemy import and_

from Library.extensions import orm
from Library.OrmModel.User import User
from Library.OrmModel.Farovite import Favorite

class FavoriteDBM():
    def __init__(self):
        pass
    def Create_Favorite(self,
                        owner_id,
                        url,
                        project_id,
                        origin,
                        catalog,
                        name,
                        description,
                        tags,
                        permission,
                        is_recommended,
                        is_unread):
        # data = {'url': 'url'}
        fav = Favorite(owner_id=owner_id,
                       url=url,
                       project_id=project_id,
                       origin=origin,
                       catalog=catalog,
                       name=name,
                       description=description,
                       tags=tags,
                       permission=permission,
                       is_recommended=is_recommended,
                       is_unread=is_unread)
        # fav = Favorite(owner_id='')
        orm.session.add(fav)
        orm.session.commit()
        return fav

    def query(self, data):
        sql = Favorite.query.filter(
            and_(
                Favorite.id == data.get('id'),
                Favorite.name == data.get('name')
            )
        )
        records = sql.all()
        Favorite.query.filter_by(id=data.get('id')).first()

    def Delete_Favorite(self,url,project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.url == url,
                Favorite.project_id == project_id
            )
        )
        record = sql.first()
        orm.session.delete(record)
        orm.session.commit()

    def Get_Favorite_By_ProjectId(self,project_id):
        sql=Favorite.query.filter(Favorite.project_id==project_id)
        records=sql.all()
        return records

    def Get_Favorite_By_Tags(self,tags):
        sql=Favorite.query.filter(Favorite.tags==tags)
        records=sql.all()
        return records
    
    # def get_unread_list(self):
    #     sql = Favorite.query.filter(Favorite.is_unread == False)
    #     records = sql.all()
    #     return records



    def Update_Favorite_Settings(self):
        return 0

    def Is_Url_Existed(self, url, project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.url ==  url,
                Favorite.project_id == project_id
            )
        )
        records = sql.first()
        return records

    def Is_Favorite_Name_Duplicate(self,name,project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.name == name,
                Favorite.project_id == project_id
            )
        )
        records = sql.first()
        return records


