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