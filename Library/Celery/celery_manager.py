import requests



class CeleryManager:


    FLOWER_URL = 'http://russellcloud.com:8080/'
    auth = ("russell","RussellCloud2017")

    def __init__(self, worker_name):
        self.worker_name = worker_name

    def update_max_concurrency(self,num):
        # worker_name = "celery@c4e9436b8530e4d739970e94943b18d9f-node1"
        url = self.FLOWER_URL + "api/worker/pool/autoscale/" + self.worker_name
        resp = requests.post(url,params={'min':5,'max':num},auth=self.auth)
        return resp.status_code == 200, resp.content


    def get_max_concurrency(self,routing_key, num):
        pass

