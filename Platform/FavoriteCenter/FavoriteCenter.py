# -*- coding:utf-8 -*-
from .FavoriteDBM import FavoriteDBM
from Library import ErrorDefine as _ED
from Library.Utils.log_util import LogCenter
from Library.singleton import Singleton


@Singleton
class FavoriteCenter(object):
    '''
    所有功能函数的返回值为二元元组(性能考虑），第一个值是在error_util找那个定义的错误码，第二个值是【可json序列化】的python对象。
    '''

    def __init__(self):
        self.dbm = FavoriteDBM.instance()
        self.logger = LogCenter.instance().get_logger("center", "favorite")

    def Create_Favorite(self, data):
        if not len(data.get('owner_id', '')) > 0:
            return (_ED.err_req_data,)

        if self.dbm.Is_Url_Existed(data.get("url"), data.get("project_id")):
            return (_ED.err_user_id_existed,)

        fav = self.dbm.Create_Favorite(owner_id=data.get("owner_id"),
                                       url=data.get("url"),
                                       project_id=data.get("project_id"),
                                       origin=data.get("origin"),
                                       source=data.get('source'),
                                       catalog=data.get("catalog"),
                                       name=data.get("name"),
                                       description=data.get("description"),
                                       tags=data.get("tags"),
                                       is_private=data.get("is_private"),
                                       is_recommended=data.get("is_recommended"),
                                       is_unread=data.get("is_unread"))
        if fav:
            out_data = fav.to_dict()
        else:
            return _ED.err_sys,

        return (_ED.no_err, out_data)

    def Update_Favorite(self, data):
        fav_id = data.get('id')
        if not fav_id:
            return (_ED.err_req_data,)
        fav = self._Get_Favorite_By_Id(fav_id)
        if not fav:
            return (_ED.err_not_found,)
        flag = self.dbm.Update_Favorite(id=fav_id,
                                        tags=data.get('tags'),
                                        catalog=data.get('catalog'),
                                        )
        if not flag:
            return (_ED.err_sys,)
        else:
            return (_ED.no_err,)

    def Delete_Favorite(self, data):
        results = {'code': _ED.no_err, 'data': ''}
        if 'owner_id' not in data:
            return "owner_id is needed"
        if "project_id" not in data:
            return "projec_id is needed"
        if "url" not in data:
            return "url is needed"
        if not self.dbm.Is_Url_Existed(data.get("url"), data.get("project_id")):
            return _ED.Respond_Err(_ED.err_not_found, "Favorite not found")
        self.dbm.Delete_Favorite(data.get("url"), data.get("project_id"))
        return results

    def Query_Favorite_By_ProjectId(self, data):
        favorites = self.dbm.Get_Favorite_By_ProjectId(data)
        out_data = self.output_favorite_list(favorites)
        return (_ED.no_err, out_data)

    def Query_Favorite_By_Tags(self, data):
        result = {'code': _ED.no_err, 'data': ''}
        favorites = self.dbm.Get_Favorite_By_Tags(data)
        output = self.output_favorite_list(favorites)
        result['data'] = output
        return result

    # def query_by_unread(self):
    #     results = self.dbm.Get_Unread_List()
    #     if results:
    #         return "success"
    #     return "fail"

    def output_favorite_list(self, results):
        new_list = list()
        for result in results:
            new_list.append({
                "owner_id": result.owner_id,
                "project_id": result.project_id,
                "url": result.url,
                "origin": result.origin,
                'source': result.source,
                "catalog": result.catalog,
                "name": result.name,
                "description": result.description,
                "tags": result.tags,
                "permission": result.permission,
                "is_recommended": result.is_recommended,
                "is_unread": result.is_unread
            })
        return new_list
