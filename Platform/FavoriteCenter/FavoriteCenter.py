
from FavoriteDBM import FavoriteDBM

class FavoriteCenter(object):
    def __init__(self):
        self.dbm = FavoriteDBM()
    def add(self, data):
        if 'owner_id' not in data:
            return False

        self.dbm.add(data)
        return "success"