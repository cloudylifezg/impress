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
    sql = "select word, UNIX_TIMESTAMP(time) from impress_news_info where word in ('" + "','".join(keywords) + "') and source_id=1 group by word order by ctime"
    #print sql
    last_update_time = {}
    ret = db.select_db(sql)
    if ret:
        for data in ret:
            last_update_time[data[0]] = int(data[1])
    
    return last_update_time

def get_twitter_info(args, keywords, stime):
    sql = "select " + ",".join(args) + " from impress_news_info where word in ('" + "','".join(keywords) + "') and time>='" + stime + "' and source_id=1 "
    twitter_info = {}
    ret = db.select_db(sql)
    doc_list = []
    if ret:
        for data in ret:
            if data[0] in twitter_info:
                twitter_info[data[0]].append(data[1])
            else:
                twitter_info[data[0]] = []
                twitter_info[data[0]].append(data[1])
            doc_list.append(str(data[2]))
    
    return twitter_info, doc_list

def get_comment_info(doc_id_list):
    sql = "select count(*) as count, doc_id from impress_news_detail where doc_id in (" + ",".join(doc_id_list) + ") and source_id=1 group by doc_id"
    comment_info = {}
    ret = db.select_db(sql)
    if ret:
        for data in ret:
            comment_info[data[1]] = int(data[0])-1
            
    return comment_info

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
        news_info.append(['1', str(twitter['tid']), twitter['category'], twitter['author'], keyword, abstract, str(twitter['repost']), '0', '0', twitter['url'], str(twitter['time']), '0', twitter['title']]) 
    
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
            news_info.append(['1', str(twitter['tid']), twitter['category'], twitter['author'], keyword, twitter['abstract'], str(twitter['repost']), '0', '0', twitter['url'], str(twitter['time']), '0', twitter['title']]) 
        insert_news_info(news_info)
        
    return True
        
def tianya_crawler_all(keywords):
    if len(keywords) <= 0:
        return False
    
    for keyword in keywords:
        twitter_info, comment_info = crawler.crawl_twitter_all(keyword)

        news_info = []
        for twitter in twitter_info:
            news_info.append(['1', str(twitter['tid']), twitter['category'], twitter['author'], keyword, twitter['abstract'], str(twitter['repost']), '0', '0', twitter['url'], str(twitter['time']), '0'], twitter['title']) 
        #self.db.insert_db('impress_news_detail', ['doc_id', 'doc_type', 'title', 'content', 'title_url', 'author_homepage', 'ip', 'time', 'uid', 'source_id', 'famous'], news_detail) 
        insert_news_info(news_info)
        
    return news_info

def tianya_crawler_comment(keywords, stime):
    if len(keywords) <= 0:
        return False
    args = ['word', 'source', 'news_id']
    twitter_info, data = get_twitter_info(args, keywords, stime)
    for keyword in keywords:
        if keyword not in twitter_info:
            continue
        news_detail, news_info = crawler.process_twitter(twitter_info[keyword])

        insert_news_detail(news_detail)
        
    return None

def tianya_crawler_update_comment(keywords, stime):
    if len(keywords) <= 0:
        return False
    args = ['word', 'source', 'news_id']
    twitter_info, doc_ids = get_twitter_info(args, keywords, stime)
    comment_info = get_comment_info(doc_ids)

    for keyword in keywords:
        if keyword not in twitter_info:
            continue
        news_detail, news_info = crawler.process_twitter(twitter_info[keyword], comment_info)

        insert_news_detail(news_detail)
        if news_info:
            update_news_comment(news_info)
        
    return news_detail

def insert_news_info(news_info):
    db.insert_db('impress_news_info', ['source_id', 'news_id', 'category', 'author', 'word', 'abstract', 'comment', 'repost', 'like', 'source', 'time', 'read', 'title'], news_info)
    
def insert_news_detail(news_detail):
    db.insert_db('impress_news_detail', ['doc_id', 'doc_type', 'content', 'surl', 'author_homepage', 'ip', 'time', 'uid', 'source_id', 'famous', 'read', 'like', 'index', 'to_index', 'platform'], news_detail)
    
def update_news_comment(news_info):
    sql = "select comment, doc_id from impress_news_info where news_id in (" + ",".join([str(k) for k in news_info.keys()]) + ") and source=1"
    ret = db.select_db(sql)
    if ret:
        for data in ret:
            comment_info[data[1]] = data[0]
            
    for info in news_info.keys():
        if info in comment_info and news_info[info] <= comment_info[info]:
            continue
        sql = "update impress_news_info set comment=%d where source=1 and news_id=%d" % (news_info[info], info)
        print sql
        db.excute_sql(sql)