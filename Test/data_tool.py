#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

sys.path.append("..")
import MySQLdb


def change_mysql_coding():
    host = "localhost"
    passwd = "zuiwan2018"
    user = "zuiwan"
    dbname = "zuiwan"

    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname)
    cursor = db.cursor()

    cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'" % dbname)

    sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % dbname
    cursor.execute(sql)

    results = cursor.fetchall()
    for row in results:
        sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
        cursor.execute(sql)
    db.close()

    celeryMsgProto = {
        "args": ('App.aliyun_api.checkInstance', '93db85b1-28d5-4e19-9eee-80588fbfedd3',
                 {'origin': 'gen25458@iZuf6abi5ju3zkr4s85m6fZ',
                  'lang': 'py',
                  'task': 'App.aliyun_api.checkInstance',
                  'group': None,
                  'root_id': '93db85b1-28d5-4e19-9eee-80588fbfedd3',
                  u'delivery_info': {u'priority': 0, u'redelivered': None, u'routing_key': 'cpu', u'exchange': u''},
                  'expires': None,
                  u'correlation_id': '93db85b1-28d5-4e19-9eee-80588fbfedd3',
                  'retries': 0,
                  'timelimit': [None, None],
                  'argsrepr': "['005aff03e0524920b7a4d1386b886b04', 172800]",
                  'eta': None,
                  'parent_id': None,
                  u'reply_to': '227beeb6-f7b8-30a3-951c-d51bf55c0998',
                  'id': '93db85b1-28d5-4e19-9eee-80588fbfedd3',
                  'kwargsrepr': '{}'
                  },
                 '[["005aff03e0524920b7a4d1386b886b04", 172800], {}, {"chord": null, "callbacks": null, "errbacks": null, "chain": null}]',
                 'application/json',
                 'utf-8'),
        "kwargs": {}
    }
