#!/usr/local/bin/python
#encoding=utf8

'''
新浪微博页面抓取
'''

#from HTMLParser import HTMLParser
from sgmllib import SGMLParser

class Sina_Weibo_Parser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.links = []
        
    def unknown_starttag(self, tag, attrs):
        if tag == 'dl':
            #print "start tag: %s" % tag
            if len(attrs) == 0:
                pass
            else:
                for (key, value) in attrs:
                    if key == 'class' and value == 'feed_list':
                        element = {'end':0}
                        self.links.append(element)
            if self.links:
                self.links[-1]['end'] += 1
                
        if self.links and self.links[-1]['end']>0 and tag == 'a':
            if len(attrs) == 0:
                pass
            else:
                for (key, value) in attrs:
                    if self.links and key == 'nick-name':
                        self.links[-1]['nick'] = value
                    if self.links and 'weibo' not in self.links[-1] and key == 'href':
                        self.links[-1]['weibo'] = value
                    if self.links and key == 'date':
                        self.links[-1]['time'] = value[0:10]
                        
    def handle_data(self, data):
        if self.links and self.links[-1]['end']>0:
            #print "end: %d, data: %s"  % (self.links[-1]['end'], data)
            if 'content' in self.links[-1]:
                self.links[-1]['content'] += data
            else:
                self.links[-1]['content'] = data
    
    def unknown_endtag(self, tag):
        if tag == 'dl' and self.links:
            self.links[-1]['end'] -= 1
            #print "end tag: %s" % tag

