#!/usr/local/bin/python
#encoding:utf8
'''
Created on 2013-12-17

@author: zhanggui
helper function for mysql db
'''

import sys, os
import MySQLdb

IMPRESS_DB_HOST = 'localhost'
IMPRESS_DB_PORT = 3306
IMPRESS_DB_USER = 'dbwriter'
IMPRESS_DB_PASSWD = 'dbwriter'
IMPRESS_DB_NAME = 'impress'

ENV_INFO = {'pro':(IMPRESS_DB_HOST, IMPRESS_DB_PORT, IMPRESS_DB_USER, IMPRESS_DB_PASSWD, IMPRESS_DB_NAME)}

class dbhelper(object):
    '''
    mysql db operation helper
    '''

    def __init__(self, env='pro'):
        if env not in ENV_INFO:
            env = 'pro'
        self.host, self.port, self.user, self.passwd, self.dbname = ENV_INFO[env]
        if not self.connect_db():
            print "connect db error!\n"
            sys.exit()
    
    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except MySQLdb.Error, ex:
            print "%s" % (ex.message)
            
        
    def connect_db(self):
        try:
            self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.dbname)
            self.cursor = self.conn.cursor()
        except MySQLdb.Error, ex:
            print "ERROR in connecting to db(%s,%d,%s,%s,%s), error message: %s" % (self.host, self.port, self.user, self.passwd, self.dbname, ex.message)
            return False
        return True
    
    def insert_db(self, table, keys, values):
        sql = "insert into %s(%s) values('" % (table, ",".join(keys))
        for v in values:
            sql += "','".join(v)
            sql += "'),('"
        sql = sql.strip(",('")
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except MySQLdb.Error, ex:
            print "ERROR in excuting sql: %s, error message: %s" % (sql, ex.message)
            return False
        return True
    
    def select_db(self, table, ):
        pass
    
    def excute_sql(self, sql):
        try:
            self.cursor.excute(sql)
            self.conn.commit()
        except MySQLdb.Error, ex:
            print "ERROR in excuting sql: %s, error message: %s" % (sql, ex.message)
            return False
        return True
        
    def conn_cursor(self):
        return self.conn, self.cursor
    
#if __name__ == '__main__':   
#    db = dbhelper()
#    keys = ('createtime', 'page_num', 'cpc_count', 'total_count', 'word_name')
#    values = [('2013-11-24 00:00:00', '0', '1', '10', '测试'),('2013-11-24 00:00:00', '1', '1', '10', '测试')]
#    db.insert_db('search_mobile_cpc_fillrate', keys, values) 