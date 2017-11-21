
from FavoriteDBM import FavoriteDBM
from Library import error_util as ED

class FavoriteCenter(object):
    def __init__(self):
        self.dbm = FavoriteDBM()

    def Create_Favorite(self, data):
        if 'owner_id' not in data:
            return "owner_id is needed"
        if "project_id" not in data:
            return "projec_id is needed"
        if "url" not in data:
            return "url is needed"
        if self.dbm.Is_Url_Existed(data.get("url"),data.get("project_id")):
            return "this url has existed"
        if data.get("name") is not None and self.dbm.Is_Favorite_Name_Duplicate(data.get("name"),data.get("project_id")):
            return "this name has existed"
        fav=self.dbm.Create_Favorite(data.get("owner_id"),
                                 data.get("url"),
                                 data.get("project_id"),
                                 data.get("origin"),
                                 data.get("catalog"),
                                 data.get("name"),
                                 data.get("descrption"),
                                 data.get("tags"),
                                 data.get("permission"),
                                 data.get("is_recommended"),
                                 data.get("is_unread"))
        results={'code':ED.no_err}
        if fav:
            results['data']=fav.to_dict()
        else:
            results=ED.Respond_Err(ED.err_sys)
        return results


    def Delete_Favorite(self,data):
        results={'code':ED.no_err,'data':''}
        if 'owner_id' not in data:
            return "owner_id is needed"
        if "project_id" not in data:
            return "projec_id is needed"
        if "url" not in data:
            return "url is needed"
        if not self.dbm.Is_Url_Existed(data.get("url"),data.get("project_id")):
            return ED.Respond_Err(ED.err_not_found,"Favorite not found")
        self.dbm.Delete_Favorite(data.get("url"),data.get("project_id"))
        return results


    def Query_Favorite_By_ProjectId(self,data):
        # results = self.dbm.Get_Favorite_By_ProjectId(data)
        # output = self.output_favorite_list(results)
        # return output
        # return output
        result={'code':ED.no_err,'data':''}
        favorites = self.dbm.Get_Favorite_By_ProjectId(data)
        output = self.output_favorite_list(favorites)
        result['data']=output
        return result

    def Query_Favorite_By_Tags(self,data):
        result = {'code': ED.no_err, 'data': ''}
        favorites = self.dbm.Get_Favorite_By_Tags(data)
        output = self.output_favorite_list(favorites)
        result['data'] = output
        return result

    # def query_by_unread(self):
    #     results = self.dbm.get_unread_list()
    #     if results:
    #         return "success"
    #     return "fail"


    def output_favorite_list(self,results):
        new_list = list()
        for result in results:
            new_list.append({
                "owner_id":result.owner_id,
                "project_id":result.project_id,
                "url":result.url,
                "origin":result.origin,
                "catalog":result.catalog,
                "name":result.name,
                "description":result.description,
                "tags":result.tags,
                "permission":result.permission,
                "is_recommended":result.is_recommended,
                "is_unread": result.is_unread
            })
        return new_list



