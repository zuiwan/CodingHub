
from FavoriteDBM import FavoriteDBM

class FavoriteCenter(object):
    def __init__(self):
        self.dbm = FavoriteDBM()
    def add(self, data):
        if 'owner_id' not in data:
            return "owner_id is needed"
        if "project_id" not in data:
            return "projec_id is needed"
        if "url" not in data:
            return "url is needed"
        if self.dbm.Is_Url_Existed(data.get("url"),data.get("project_id")):
            return "this url has existed"
        self.dbm.add(data)
        return "success"


    def delete(self,data):
        if 'owner_id' not in data:
            return "owner_id is needed"
        if "project_id" not in data:
            return "projec_id is needed"
        if "url" not in data:
            return "url is needed"
        if self.dbm.Is_Url_Existed(data.get("url"),data.get("project_id")):
            self.dbm.delete(data.get("url"),data.get("project_id"))
            return "success"
        else:
            return "this url does not exist"


    def query_by_project(self,data):
        results=self.dbm.query_by_project(data)
        output = self.output_favorite_list(results)
        return output

    def query_by_tags(self,data):
        results=self.dbm.query_by_tags(data)
        output=self.output_favorite_list(results)
        return output

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



