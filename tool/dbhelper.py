#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       dbhelper
   Description:
   Author:          huangzhen
   date:            2018/3/23
-------------------------------------------------
   Change Activity:
                   2018/3/23:
-------------------------------------------------
"""
__author__ = 'huangzhen'

def change_mysql_coding():
    import MySQLdb
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
      sql = "ALTER TABLE `%s` CONVERT to character set DEFAULT COLLATE DEFAULT" % (row[0])
      cursor.execute(sql)
    db.close()
