
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
        if "project_id" not in data:
            return "this project does not existed"
        result=self.dbm.query_by_project(data.get("project_id"))
        return result



