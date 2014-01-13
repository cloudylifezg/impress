#!/usr/local/bin/python
#encoding=utf8

import sys,os
import urllib
from urlparse import urlparse
from sets import Set
import chardet
import time
import datetime
#import re
from tianya_html_parser import *

txt_format1 = ['title', 'abstract', 'category', 'author', 'time', 'repost']
txt_format2 = ['title', 'category', 'author', 'time', 'repost']

#total_re = re.compile('.*([0-9]+).*')

class TianYa_Api(object):
    def __init__(self, db=None):
        self.search_url = 'http://search.tianya.cn/bbs?q=%s&pn=%d&s=4'
        self.db = db
        self.last_time = 0
        self.keyword = ''
        self.max_document = 30

    def __html_decode(self):
        encode_method = chardet.detect(self.content)
        if encode_method['encoding'].lower() == 'utf-8':
            pass
        else:
            self.content = self.content.decode('gb2312', 'ignore').encode('utf-8')
                    
    #定制数目抓取
    def crawl_twitter(self, offset, limit, keyword):
        self.keyword = keyword
        offset = offset if offset >= 0 else 0
        limit = limit if limit > 0 else 20
        total_page = int(round(limit/10))
        for page in range(1, total_page):
            print "page: %d" % page
            search_url = self.search_url % (self.keyword, page)
        
            #try:
            cursor = urllib.urlopen(search_url)
            self.content = cursor.read()
            self.__html_decode()
            self.extract_twitter()
            #except Exception,ex:
            #    print "get url %s error: %s" % (self.search_url, ex)
    
    #增量抓取
    def crawl_twitter_update(self, keyword):
        page = 1
        while True:
            print "page: %d" % page
            search_url = self.search_url % (keyword, page)
        
            try:
                cursor = urllib.urlopen(search_url)
                if cursor.getcode() != 200:
                    break
                self.content = cursor.read()
                self.__html_decode()
                ret = self.extract_twitter()
                if ret != 0:
                    break;
            except Exception,ex:
                print "get url %s error: %s" % (self.search_url, ex)
      
            page += 1
            
    #全量抓取, type, 1为只抓取twitter基本信息， 2为抓取评论等信息
    def crawl_twitter_all(self, keyword, type=1):
        page = 1
        search_url = self.search_url % (keyword, page)
        
        try:
            cursor = urllib.urlopen(search_url)
            if cursor.getcode() != 200:
                return []
            self.content = cursor.read()
            self.__html_decode()
            total_count = self.get_twitter_info()
        except Exception,ex:
            print "get url %s error: %s" % (self.search_url, ex)
            sys.exit()
        
        if total_count <= 0:
            return []
        
        total = total_count if total_count <= self.max_document or self.max_document == 0 else self.max_document
        
        total_page = total/20
        self.result_twitter = []
        self.result_comment = []
        self.tid_set = Set([])
        while page <= total_page:
            print "page: %d" % page
            search_url = self.search_url % (keyword, page)
        
            try:
                cursor = urllib.urlopen(search_url)
                if cursor.getcode() != 200:
                    break
                self.content = cursor.read()
                if len(self.content) == 0:
                    break
                self.__html_decode()
                ret = self.extract_twitter()
                if ret != 0:
                    break
            except Exception,ex:
                print "get url %s error: %s" % (self.search_url, ex)
                sys.exit()
            
            page += 1
        
        if type == 2:
            self.process_twitter()
        return self.result_twitter, self.result_comment
        
    def get_twitter_info(self):
        parser = TianYa_HTML_Parser()
        parser.feed(self.content)
        parser.close()
        page_content = parser.page_content.strip()
        if len(page_content) > 0:
            total_content = page_content.split("\n")[0].strip(" \n\r").strip('共有条内容')
            return int(total_content)
            
        return total_content
        
    def extract_twitter(self):
        parser = TianYa_HTML_Parser()
        parser.feed(self.content)
        parser.close()
        if len(parser.links) <= 0:
            return 1        #抓取内容为空
        for link in parser.links:
            if 'content' not in link or len(link['content']) == 0:
                continue
            values = [info.strip() for info in link['content'].strip().split("\n") if len(info.strip()) != 0]
            keys = txt_format1 if len(values) == 6 else txt_format2
            item = dict(zip(keys, values))
            for key in item.keys():
                if key in Set(['category', 'author', 'time', 'repost']):
                    pos = item[key].find('：')
                    if pos != -1:
                        item[key] = item[key][(pos+3):]
            
            if 'url' not in link:
                continue
            item['url'] = link['url']
            item['time'] = item['time'] + ':00'
            item['tid'] = self.extract_twitter_info(item['url'])[0]
            if str(item['tid']) + "_" + item['time'] in self.tid_set:
                continue
            self.tid_set.add(str(item['tid']) + "_" + item['time']) 
            date_time = datetime.datetime.strptime(item['time'], "%Y-%m-%d %H:%M:%S")
            doc_time = int(time.mktime(date_time.timetuple()))
            if doc_time <= self.last_time:
                #已到上次抓取的
                return 2   
            self.result_twitter.append(item)
       
        return 0   
    
    def extract_post(self, parser):
        #parser = TianYa_Poster_HTML_Parser()
        parser.feed(self.content)
        #parser.close()
        #print "content:%s, detail:%s" % (parser.element['content'].strip(), parser.detail.strip())
        detail_info = parser.detail.strip().split("\n")
        if detail_info > 0:
            click = detail_info[2]
            pos = click.find('：')
            if pos != -1:
                 click = click[(pos+3):]
        
        try:
            click = int(click)
        except Exception,ex:
            click = 0
        return (parser.element['content'].strip()[0:3000], click, parser.uid, parser.famous)
    
    #http://bbs.tianya.cn/post-free-2366245-1.shtml
    def extract_twitter_info(self, url):
        o = urlparse(url)
        path = o.path.strip("/")
        pos = path.find(".")
        info = path[:pos].split('-')
        try:
            if len(info) >= 3:
                tid = int(info[2])
            preffix = o.hostname + "/" + "-".join(info[0:3]) + "-"
            suffix = path[pos:]
        except Exception,ex:
            pass
        
        return (tid, preffix, suffix)
    
    def process_twitter(self):       
        #self.result_twitter.reverse()
        if len(self.result_twitter) == 0:
            print "no update"
            return False
        news_info = []
        news_detail = []
        comment_url = []
        parser = TianYa_Poster_HTML_Parser()
        for item in self.result_twitter:
            try:
                cursor = urllib.urlopen(item['url'])
                self.content = cursor.read()
                self.__html_decode()
            except Exception,ex:
                print "get url %s error: %s" % (item['url'], ex)
            
            content, click, uid, famous = self.extract_post(parser)
            poster_url = self.extract_twitter_info(item['url'])
            news = ['1', str(poster_url[0]), item['category'], item['author'], self.keyword, self.keyword, str(item['repost']), '0', '0', item['url'], str(item['time']), str(click)]
            news_info.append(news)
            detail = [str(poster_url[0]), '1', item['title'], content, item['url'], 'http://www.tianya.cn/' + uid, '', str(item['time']), str(uid), '1', str(famous)]
            news_detail.append(detail)
            comment_url.append([poster_url[1], poster_url[2]])
           
        parser.close()
        #print "start to insert info to db"
        #self.db.insert_db('bak_impress_news_info', ['source_id', 'news_id', 'category', 'author', 'word', 'keywords', 'comment', 'repost', 'like', 'source', 'time', 'read'], news_info)
        #self.db.insert_db('bak_impress_news_detail', ['doc_id', 'doc_type', 'title', 'content', 'title_url', 'author_homepage', 'ip', 'time', 'uid', 'source_id', 'famous'], news_detail)
        #for url in comment_url:
        #    self.crawl_comment(url)
        
    def crawl_comment(self, url_info, limit=20):
        page = 1
        limit = limit if limit > 0 else 20
        parser = TianYa_Comment_HTML_Parser()
        while True:
            comment_url = "http://" + url_info[0] + str(page) + url_info[1]
            print comment_url
            try:
                cursor = urllib.urlopen(comment_url)
                if cursor.getcode() != 200:
                    break
                self.content = cursor.read()
                self.__html_decode()
                self.extract_comment(parser, page)
            except Exception,ex:
                print "get url %s error: %s" % (comment_url, ex)
                break
            page += 1
    
        parser.close()
        
    def extract_comment(self, parser, page):   
         parser.feed(self.content)
         offset = 0 if page > 1 else 1
         comment_list = []
         if len(parser.links) > 0:
             for link in parser.links[offset:]:
                 if 'content' not in link:
                     continue
                 parts =  link['content'].strip().split("\n")
                 item = []
                 for p in parts:
                     info = p.strip().strip('举报').strip('回复')
                     if len(info) == 0:
                         continue
                     if len(item) < 3:
                         pos = info.rfind("：")
                         if pos != -1:
                             info = info[pos+3:]
                     item.append(info)
                 try:
                     uid = int(link['uid']) if 'uin' in link else 0
                 except Exception, ex:
                     pass
                 
                 date_time = datetime.datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
                 time = int(time.mktime(date_time.timetuple()))
                 item.append(uid)
                 comment_list.append(item)       
            
#crawler = TianYa_Api()
#keywords = ['方舟子']
#for keyword in keywords:
#    crawler.crawl_twitter(0, 20, keyword)
    #crawler.extract_twitter()
