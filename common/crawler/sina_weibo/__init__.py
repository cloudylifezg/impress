#!/usr/local/bin/python
#encoding=utf8

import sys
from sina_weibo_api import Sina_Weibo_Api

data_file = "/Users/zhanggui/source/impress/data/sina_weibo_%s.txt"
sina_weibo_crawler = Sina_Weibo_Api("/Users/zhanggui/source/impress/data/sina_weibo.txt")

def sina_weibo_crawler(keywords, db):
    crawler = Sina_Weibo_Api(data_file)
    if len(keywords) <= 0:
        return False
    for keyword in keywords:
        data_file = "/Users/zhanggui/source/impress/data/sina_weibo_%s.txt" % keyword
        crawler.crawl_twitter(0, 20, keyword, data_file)
        crawler.extract_twitter()
    
    return True