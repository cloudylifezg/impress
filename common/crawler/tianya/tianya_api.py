#!/usr/local/bin/python
#encoding=utf8

import sys,os
import urllib
from urlparse import urlparse
from sets import Set
import chardet
import time
import datetime
import re
from tianya_html_parser import *
import unicodedata

txt_format1 = ['title', 'abstract', 'category', 'author', 'time', 'repost']
txt_format2 = ['title', 'category', 'author', 'time', 'repost']

comment_re = re.compile(r"([0-9]+楼)")

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
    
    def extract_post(self):
        parser = TianYa_Poster_HTML_Parser()
        parser.feed(self.content)
        #print "content:%s, detail:%s" % (parser.element['content'].strip(), parser.detail.strip())
        detail_info = parser.detail.strip().replace(' 时间', '\n时间').split("\n")
        post_info = {}
        #print parser.detail.strip()
        if len(detail_info) > 0:
            for d in detail_info:
                pos = d.rfind('：')
                if pos != -1:
                    post_info[d[0:pos].strip()] = d[(pos+3):].strip()
        
        try:
            comment = int(post_info['回复']) if '回复' in post_info else 0
            click = int(post_info['点击']) if '点击' in post_info else 0
            platform = post_info['来自'] if '来自' in post_info else 'pc'
            time = post_info['时间'] if '时间' in post_info else '1970-01-01 00:00:00'
        except Exception,ex:
            comment = 0
            click = 0
            platform = 'pc'
            time = ''
            
        content = parser.element['content'].strip() if parser.element and 'content' in parser.element else ''
        uid = parser.uid if parser.uid else '0'
        famous = parser.famous if parser.famous else '0'
        
        parser.close()
        return (content, click, uid, famous, comment, platform, time)
    
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
    
    #type1， 只抓正文， 2， 同时抓评论数
    def process_twitter(self, twitters, comment_info={}, type=2, limit=0):
        if len(twitters) == 0:
            return False
        self.news_info = {}
        self.news_detail = []
        #parser = TianYa_Poster_HTML_Parser()
        #if type == 2:
        #    comment_parser = TianYa_Comment_HTML_Parser()
        for source in twitters:
            #source = "http://bbs.tianya.cn/post-funinfo-4979418-1.shtml"
            try:
                cursor = urllib.urlopen(source)
                self.content = cursor.read()
                self.__html_decode()
            except Exception,ex:
                print "get url %s error: %s" % (source, ex)
                continue
            
            content, click, uid, famous, comment, platform, time = self.extract_post()
            poster_url = self.extract_twitter_info(source)
            
            if poster_url[0] in comment_info:
                detail = [str(poster_url[0]), '1', content, source, 'http://www.tianya.cn/' + uid, '', time, uid, '1', famous, str(click), '0', '0', '0', platform]
                self.news_detail.append(detail)
            
            #if poster_url[0] in comment_info and (comment - comment_info[poster_url[0]]) < 10:
            #    continue
            self.news_info[poster_url[0]] = comment
            if type==2 and comment > 0:
                page = comment_info[poster_url[0]]/100 + 1 if poster_url[0] in comment_info else 1
                #total = limit if limit != 0 and limit < comment else comment
                #print comment, limit
                while (page-1)*100 < comment:
                    comment_url = "http://" + poster_url[1] + str(page) + poster_url[2]
                    print comment_url
                    #comment_url = "http://bbs.tianya.cn/post-funinfo-4949828-1.shtml"
                    offset = comment_info[poster_url[0]] + 1 if poster_url[0] in comment_info else 1
                    self.crawl_comment(comment_url, poster_url[0], page, offset)
                    page += 1
        
        return self.news_detail, self.news_info
        
    def crawl_comment(self, comment_url, doc_id, page=1, offset=1):
        parser = TianYa_Comment_HTML_Parser()
        try:
            cursor = urllib.urlopen(comment_url)
            if cursor.getcode() != 200:
                return 
            self.content = cursor.read()
            self.__html_decode()
            #self.extract_comment(parser)
            parser.feed(self.content)
            if len(parser.links) > 0:
                index = (page-1)*100+1
                for link in parser.links:
                    if 'content' not in link or index==1 or index <= offset:
                        index += 1
                        continue
                    
                    parts = link['content'].strip().split("\n")
                    
                    post_info = {}
                    for p in parts[0:(len(parts)-1)]:
                        info = p.strip()
                        pos = info.rfind('：')
                        if pos != -1:
                            item = info.replace(' 时间', '\n时间').split("\n")
                            for i in item:
                                n_pos = i.rfind('：')
                                post_info[i[0:n_pos].strip()] = i[(n_pos+3):].strip()
                    
                    time = post_info['时间'] if '时间' in post_info else '1970-01-01 00:00:00'
                    platform = post_info['来自'] if '来自' in post_info else 'pc'
                            
                    try:
                        uid = link['uid'] if 'uid' in link else '0'
                    except Exception, ex:
                        pass
                    
                    famous = link['famous'] if 'famous' in link else '0'
                    
                    to_index = 1
                    parts[-1] = parts[-1]
                    pos = parts[-1].find("楼")
                    content = parts[-1]
                    if pos != -1:
                        comment_match = re.findall(comment_re, parts[-1])
                        w_pos = 0
                        if comment_match:
                            match_word = comment_match[-1]
                            to_index = int(match_word.strip('楼'))
                            w_pos = parts[-1].rfind(match_word)
                            if w_pos != -1:
                                parts[-1] = parts[-1][w_pos:]
                        if to_index != 1:
                            if parts[-1].rfind('-----') != -1:
                                n_pos = parts[-1].rfind('-----')
                                parts[-1] = parts[-1][n_pos:].strip('- ')
                            if parts[-1].rfind('=====') != -1:
                                n_pos = parts[-1].rfind('=====')
                                parts[-1] = parts[-1][n_pos:].strip('= ')
                            if parts[-1].find('　　') != -1:
                                n_pos = parts[-1].find('　　')
                                parts[-1] = parts[-1][n_pos:].strip('　')
                    
                    detail = [str(doc_id), '2', parts[-1].strip().replace("'", "").replace("\\", ""), comment_url, 'http://www.tianya.cn/' + uid, '', time, uid, '1', famous, '0', '0', str(index), str(to_index), 'pc']
                    self.news_detail.append(detail) 
                    index += 1
                    
        except Exception,ex:
            print "get url %s error: %s" % (comment_url, ex)
        
        parser.close()
        
    def extract_comment(self, parser):   
         parser.feed(self.content)
         comment_list = []
         if len(parser.links) > 0:
             for link in parser.links:
                 if 'content' not in link:
                     continue
                 
                 parts =  link['content'].strip().split("\n")
                 time = ''
                 for p in parts:
                     info = p.strip().strip('举报').strip('回复')
                     if len(info) == 0:
                         continue
                     if len(item) < 3:
                         pos = info.rfind("：")
                         if pos != -1:
                             item[info[:pos]] = info[pos+3:]
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
