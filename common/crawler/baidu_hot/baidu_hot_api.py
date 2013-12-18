#!/usr/local/bin/python
#encoding=utf8

import sys,os
import urllib
from sets import Set
import chardet
import time
import datetime
from tianya_html_parser import TianYa_HTML_Parser

txt_format1 = ['title', 'abstract', 'category', 'author', 'time', 'repost']
txt_format2 = ['title', 'category', 'author', 'time', 'repost']

class TianYa_Api(object):
    def __init__(self):
        self.search_url = 'http://search.tianya.cn/bbs?q=%s&pn=%d&s=4'
    
    def parse_last_time(self):
        file = open(self.file, 'r')
        i = -1
        try:
            while True:
                i = i - 1
                file.seek(i, os.SEEK_END)
                if file.read(1) == '\n':
                    break
            line = file.readline().strip()
        
            self.last_time = int(line.split('    ')[-2])
            #print "last time: %d" % self.last_time
        except:
            self.last_time = 0
        file.close()
        
    def crawl_twitter(self, offset, limit, keyword, date_file):
        offset = offset if offset >= 0 else 0
        limit = limit if limit > 0 else 0
        total_page = int(round(limit/10))
        for page in range(1, total_page):
            print "page: %d" % page
            search_url = self.search_url % (keyword, page)
            self.file = date_file
            #if os.path.isfile(self.file):
            #    self.parse_last_time()
        
            try:
                cursor = urllib.urlopen(search_url)
                self.content = cursor.read()
                self.__html_decode()
                if not self.extract_twitter():
                    break
            except Exception,ex:
                print "get url %s error: %s" % (self.search_url, ex)
            
    def __html_decode(self):
        encode_method = chardet.detect(self.content)
        if encode_method['encoding'].lower() == 'utf-8':
            pass
        else:
            self.content = self.content.decode('gb2312', 'ignore').encode('utf-8')
        #self.content = urllib.unquote(self.content.replace('\/', '/')).decode('unicode_escape')
        #self.content = urllib.unquote(self.content.encode('utf8'))
    
    def extract_twitter(self):
        parser = TianYa_HTML_Parser()
        parser.feed(self.content)
        parser.close()
        file = open(self.file, 'a+')
        self.twitter = []
        if len(parser.links) <= 0:
            return False
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
                        
            date_time = datetime.datetime.strptime(item['time'] + ":00", "%Y-%m-%d %H:%M:%S")
            item['time'] = str(int(time.mktime(date_time.timetuple())))
            #print " ".join(item.values())
            self.twitter.append(item)
        self.twitter.reverse()
        for t in self.twitter:
            file.write("    ".join(t.values()) + "\n") 
        file.close() 
        return True           

crawler = TianYa_Api()
keywords = ['爸爸去哪儿']
for keyword in keywords:
    data_file = "/Users/zhanggui/source/impress/data/sina_weibo_%s.txt" % keyword
    crawler.crawl_twitter(0, 5000, keyword, data_file)
    #crawler.extract_twitter()

