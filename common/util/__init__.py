#!/usr/local/bin/python
#encoding=utf8

'''
Created on 2013-12-17

@author: zhanggui
helper function for mysql db
'''
import sys
from dbhelper import dbhelper
import MySQLdb

db = dbhelper()

def db_insert(table, keys, values):
    sql = "insert into %s(%s) values('" % (table, ",".join(keys))
    for v in values:
        sql += "','".join(v)
        sql += "'),('"
    sql = sql.strip(",('")
    sql += ')'
    try:
        conn,cursor = db.conn_cursor()
        cursor.execute(sql)
        conn.commit()
    except MySQLdb.Error, ex:
        print "ERROR in excuting sql: %s, error message: %s" % (sql, ex.message)
        return False
        
def db_excute(sql):
    if sql == "":
        return False
    try:
        conn,cursor = db.conn_cursor()
        cursor.execute(sql)
        conn.commit()
    except MySQLdb.Error, ex:
        print "ERROR in excuting sql: %s, error message: %s" % (sql, ex.message)
