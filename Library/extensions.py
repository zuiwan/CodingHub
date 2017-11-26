#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.celery_util import make_celery
from Application.app import flask_app

celery_app = make_celery(flask_app)

from flask_sqlalchemy import SQLAlchemy
orm = SQLAlchemy(flask_app)



from elasticsearch import Elasticsearch
# es = Elasticsearch(hosts=[{"host": "47.92.31.158", "port": 9200}])

# from sdk import GeetestLib
# pc_geetest_id = "e937ee78ecfeb8e58616478277576a9a"
# pc_geetest_key = "5d3f48c1c74de05cc028bfbdfa9740e0"
# geetest = GeetestLib(pc_geetest_id,pc_geetest_key)