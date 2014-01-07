#!/usr/local/bin/python
#encoding=utf8

import sys
from util import dbhelper
from tianya_api import TianYa_Api

db = dbhelper.dbhelper()
crawler = TianYa_Api(db)

def tianya_crawler(keywords):
    if len(keywords) <= 0:
        return False
    
    for keyword in keywords:
        crawler.crawl_twitter(0, 20, keyword)
    
    return True

def get_last_update_time(keywords):
    sql = "select keywords, UNIX_TIMESTAMP(time) from bak_impress_news_info where keywords in ('" + "','".join(keywords) + "') group by keywords order by ctime"
    last_update_time = {}
    for data in db.select_db(sql):
        last_update_time[data[0]] = int(data[1])
    
    return last_update_time

def tianya_update_crawler(keywords):
    if len(keywords) <= 0:
        return False
    
    last_update_time = get_last_update_time(keywords)
    for keyword in keywords:
        crawler.last_time = last_update_time[keyword]
        crawler.crawl_twitter_update(keyword)
        
def tianya_crawler_all(keywords):
    if len(keywords) <= 0:
        return False
    
    for keyword in keywords:
        crawler.crawl_twitter_all(keyword)
    
    return True

