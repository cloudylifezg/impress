#!/usr/local/bin/python
#encoding=utf8

'''
天涯页面抓取类
'''

#from HTMLParser import HTMLParser
from sgmllib import SGMLParser

class TianYa_HTML_Parser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.links = []
        self.search_div = 0
        self.search = False
        
    def unknown_starttag(self, tag, attrs):
        if tag == 'div':
            if len(attrs) > 0:
                for (key, value) in attrs:
                    if key == 'class' and value == 'searchListOne':
                        self.search_div += 1
                        self.search = True
                        
        if self.search and tag == 'div':
            self.search_div += 1
                        
        if self.search and tag == 'li':
            element = {'end':0}
            self.links.append(element)
            if self.links:
                self.links[-1]['end'] += 1
                        
    def handle_data(self, data):
        if self.links and self.links[-1]['end']>0:
            #print "end: %d, data: %s"  % (self.links[-1]['end'], data)
            if 'content' in self.links[-1]:
                self.links[-1]['content'] += data
            else:
                self.links[-1]['content'] = data
    
    def unknown_endtag(self, tag):
        if self.search and tag == 'div':
            self.search_div -= 1
            if self.search_div <= 0:
                self.search = False
                
        if tag == 'li' and self.links:
            self.links[-1]['end'] -= 1
            #print "end tag: %s" % tag

