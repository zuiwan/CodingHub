# -*- coding:utf-8 -*-
from sqlalchemy import or_, and_, extract, any_
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

import traceback
from Library.Utils.log_util import LogCenter
from Library.singleton import Singleton
from Library.extensions import orm
from Library.OrmModel.User import User
from Library.OrmModel.Farovite import Favorite


@Singleton
class FavoriteDBM():
    def __init__(self):
        self.logger = LogCenter.instance().get_logger("center", "favorite")
        self.db = orm

    def Create_Favorite(self,
                        owner_id,
                        url,
                        project_id,
                        origin,
                        source,
                        catalog,
                        name,
                        description,
                        tags,
                        is_recommended,
                        is_unread):
        fav = Favorite(owner_id=owner_id,
                       url=url,
                       project_id=project_id,
                       origin=origin,
                       catalog=catalog,
                       name=name,
                       source=source,
                       description=description,
                       tags=tags,
                       is_recommended=is_recommended,
                       is_unread=is_unread)
        self.db.session.add(fav)
        self.db.session.commit()
        return fav

    def Update_Favorite(self,
                        id,
                        owner_id=None,
                        catalog=None,
                        tags=None,
                        is_recommended=None,
                        is_unread=None,
                        source=None,
                        description=None,
                        ):
        fav = self._Get_Favorite_By_Id(id)
        if owner_id is not None:
            fav.owner_id = owner_id
        if tags is not None:
            fav.tags = tags
        if is_unread is not None:
            fav.is_unread = is_unread
        if catalog is not None:
            fav.catalog = catalog
        if source is not None:
            fav.source = source
        self.db.session.commit()
        return True

    def _Get_Favorite_By_Id(self, id):
        return Favorite.query.get(id)

    def query(self, data):
        sql = Favorite.query.filter(
            and_(
                Favorite.id == data.get('id'),
                Favorite.name == data.get('name')
            )
        )
        records = sql.all()
        Favorite.query.filter_by(id=data.get('id')).first()

    def Delete_Favorite(self, url, project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.url == url,
                Favorite.project_id == project_id
            )
        )
        record = sql.first()
        orm.session.delete(record)
        orm.session.commit()

    def Get_Favorite_By_ProjectId(self, project_id):
        sql = Favorite.query.filter(and_(Favorite.project_id == project_id,
                                         Favorite.is_deleted == 0))
        try:
            records = sql.all()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            records = []
        return records

    def Get_Favorite_By_Tags(self, tag):
        sql = Favorite.query.filter(and_(any_(tag, Favorite.tags),
                                         Favorite.is_deleted == 0))
        try:
            records = sql.all()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            records = []
        return records

    def Get_Unread_List(self, unread=True):
        sql = Favorite.query.filter(Favorite.is_unread == unread)
        records = sql.all()
        return records

    def Is_Url_Existed(self, url, project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.url == url,
                Favorite.project_id == project_id
            )
        )
        records = sql.first()
        return records

    def Is_Favorite_Name_Duplicate(self, name, project_id):
        sql = Favorite.query.filter(
            and_(
                Favorite.name == name,
                Favorite.project_id == project_id
            )
        )
        records = sql.first()
        return records
