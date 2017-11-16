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

    def delete(self):
        return 0

    def modify(self):
        return 0

