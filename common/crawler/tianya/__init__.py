#!/usr/local/bin/python
#encoding=utf8

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
    sql = "select word, UNIX_TIMESTAMP(time) from impress_news_info where word in ('" + "','".join(keywords) + "') group by word order by ctime"
    #print sql
    last_update_time = {}
    ret = db.select_db(sql)
    if ret:
        for data in ret:
            last_update_time[data[0]] = int(data[1])
    
    return last_update_time

def tianya_update_crawler_word(keyword, last_time, max_count=1000):
    crawler.last_time = last_time
    crawler.max_document = max_count
    last_update_time = get_last_update_time([keyword])
    print last_update_time
    if keyword in last_update_time and last_update_time[keyword]>crawler.last_time:
        crawler.last_time = last_update_time[keyword]
        
    twitter_info, comment_info = crawler.crawl_twitter_all(keyword)
    if not twitter_info:
        return 1
    news_info = []
    for twitter in twitter_info:
        abstract = twitter['abstract'] if 'abstract' in twitter else ''
        news_info.append(['1', str(twitter['tid']), twitter['category'], twitter['author'], keyword, abstract, str(twitter['repost']), '0', '0', twitter['url'], str(twitter['time']), '0']) 
    
    insert_news_info(news_info)
    
    return 0

def tianya_update_crawler_words(keywords, last_time={}, max_count=1000):
    if len(keywords) <= 0:
        return False
    
    crawler.max_document = max_count
    last_update_time = get_last_update_time(keywords)
    for keyword in keywords:
        crawler.last_time = 0
        if keyword in last_time:
            crawler.last_time = last_time[keyword]
        if keyword in last_update_time and last_update_time[keyword]>crawler.last_time:
            crawler.last_time = last_update_time[keyword]
        
        twitter_info, comment_info = crawler.crawl_twitter_all(keyword)
        if len(twitter_info) == 0:
            continue
        news_info = []
        for twitter in twitter_info:
            news_info.append(['1', str(twitter['tid']), twitter['category'], twitter['author'], keyword, twitter['abstract'], str(twitter['repost']), '0', '0', twitter['url'], str(twitter['time']), '0']) 
        insert_news_info(news_info)
        
    return True
        
def tianya_crawler_all(keywords):
    if len(keywords) <= 0:
        return False
    
    for keyword in keywords:
        twitter_info, comment_info = crawler.crawl_twitter_all(keyword)

        news_info = []
        for twitter in twitter_info:
            news_info.append(['1', str(twitter['tid']), twitter['category'], twitter['author'], keyword, twitter['abstract'], str(twitter['repost']), '0', '0', twitter['url'], str(twitter['time']), '0']) 
        #self.db.insert_db('impress_news_detail', ['doc_id', 'doc_type', 'title', 'content', 'title_url', 'author_homepage', 'ip', 'time', 'uid', 'source_id', 'famous'], news_detail) 
        insert_news_info(news_info)
        
    return news_info

def insert_news_info(news_info):
    db.insert_db('impress_news_info', ['source_id', 'news_id', 'category', 'author', 'word', 'keywords', 'comment', 'repost', 'like', 'source', 'time', 'read'], news_info)
     