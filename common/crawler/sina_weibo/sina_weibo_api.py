#!/usr/local/bin/python
#encoding=utf8

import sys,os
import urllib
from sina_weibo_login import Sina_Weibo_Login
from sina_weibo_html_parser import Sina_Weibo_HTML_Parser

weibo_format = ['nick', 'weibo', 'content', 'like', 'repost', 'comment', 'source', 'time']

#keyword_list = ['永城', '曼德拉', '林志颖', '红河', '海尔', '微信', '高晓松']
#data_file = 'weibo.dat'

class Sina_Weibo_Api(object):
    def __init__(self):
        self.url_opener = Sina_Weibo_Login().get_opener()
        self.search_url = 'http://s.weibo.com/weibo/%s&b=1&nodup=1&category=4&page=%d'
    
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
        page = offset%20+1
        search_url = self.search_url % (keyword, page)
        self.file = date_file
        if os.path.isfile(self.file):
            self.parse_last_time()
    
        try:
            cursor = self.url_opener.open(search_url)
            self.content = cursor.read()
            self.__html_decode()
        except Exception,ex:
            print "get url %s error: %s" % (self.search_url, ex)
            
    def __html_decode(self):
        self.content = urllib.unquote(self.content.replace('\/', '/')).decode('unicode_escape')
        self.content = urllib.unquote(self.content.encode('utf8'))
    
    def extract_twitter(self):
        parser = Sina_Weibo_HTML_Parser()
        parser.feed(self.content)
        parser.close()
        file = open(self.file, 'a+')
        self.twitter = []
        for link in parser.links:
            if int(link['time']) <= self.last_time:
                break
            item = {}
            for k in link.keys():
                if k != 'end' and k != 'content':
                    item[k] = link[k]
                    
            #print "%s" % link['content']
            parts = link['content'].strip().split("\n")
            item['content'] = parts[0].strip()
            item['source'] = ''
            #word = "："
            for i in range(1, len(parts)):
                p = parts[i].strip().strip('|')
                if p == "" :
                    pass
                else:
                    #offset = p.find(word)
                    #item['content'] = p
                    if p.find("赞")!=-1:
                        #print "p value: %s" % p
                        like = p.strip('赞(').strip(')')
                        item['like'] = '0' if like == "" else like
                    elif p.find("转发")!=-1:
                        repost = p.strip('转发(').strip(')')
                        item['repost'] = '0' if repost == "" else repost
                    elif p.find("评论")!=-1:
                        comment = p.strip('评论(').strip(')')
                        item['comment'] = '0' if comment == "" else comment
                    elif p.find("来自")!=-1:
                        source_info = p.split(" ")
                        if source_info:
                            item['source'] = source_info[-1].strip()
                
            #for k in item:
                 #print "%s" % item[k]
            self.twitter.append(item)
        self.twitter.reverse()
        for t in self.twitter:
            file.write("%s    %s    %s    %s    %s    %s    %s    %s\n" % (t['nick'], t['weibo'], t['content'], t['like'], t['repost'], t['comment'], t['time'], t['source'])) 
        file.close()            
            #print "%s ------> %s" % (k,link[k].strip(" \n"))      
        #print parser.links

#if __name__ == '__main__':
#    for keyword in keyword_list:
#        print keyword
#        crawler = weibo_crawler("weibo_%s.dat" % keyword)
#        crawler.crawl_twitter(0, 20, keyword)
#        crawler.extract_twitter()
    #print "content: %s" % crawler.content
    
    
