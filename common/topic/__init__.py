#!/usr/local/bin/python
#encoding=utf8

import topic
from util import dbhelper,language

db = dbhelper.dbhelper()
topic_model = topic.Topic()

def get_twitter_info(keyword, stime, etime):
    sql = "select news_id, keywords from impress_news_info where word='%s' and time>='%s' and time<='%s'" % (keyword, stime, etime)
    #print sql
    ret = db.select_db(sql)
    doc_info = []
    doc_map = {}
    if ret:
        for data in ret:
            news = language.transfer(data[1])
            doc_info.append(news)
            doc_map[data[0]] = news
             
    return doc_info, doc_map

def generate_topcs(keyword, stime, etime):
    doc_info, doc_map = get_twitter_info(keyword, stime, etime)
    kword = topic.st_keyword(keyword, set(['n', 'z']))
    topic_model.set_keyword(kword)
    topic_model.init_document(doc_info)
    
    return topic_model.extract_topic()

