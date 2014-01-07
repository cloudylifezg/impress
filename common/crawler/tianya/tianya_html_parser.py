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
        self.page_content = ''
        self.page = False
        
    def unknown_starttag(self, tag, attrs):
        if tag == 'div':
            if len(attrs) > 0:
                for (key, value) in attrs:
                    if key == 'class' and value == 'searchListOne':
                        self.search_div += 1
                        self.search = True
                    if key == 'class' and value == 'long-pages'  and not self.page:
                        self.page = True
                        
        if self.search and tag == 'div':
            self.search_div += 1
                        
        if self.search and tag == 'li':
            element = {'end':0}
            self.links.append(element)
            if self.links:
                self.links[-1]['end'] += 1
                
        if self.links and self.links[-1]['end']>0 and tag == 'a':
            if len(attrs) == 0:
                pass
            else:
                for (key, value) in attrs:
                    if self.links and key=='href' and value.find('post') != -1:
                        self.links[-1]['url'] = value
            
                        
    def handle_data(self, data):
        if self.links and self.links[-1]['end']>0:
            #print "end: %d, data: %s"  % (self.links[-1]['end'], data)
            if 'content' in self.links[-1]:
                self.links[-1]['content'] += data
            else:
                self.links[-1]['content'] = data
                
        if self.page:
            self.page_content += data
    
    def unknown_endtag(self, tag):
        if self.search and tag == 'div':
            self.search_div -= 1
            if self.search_div <= 0:
                self.search = False
                
        if self.page and tag == 'div':
            self.page = False
                
        if tag == 'li' and self.links:
            self.links[-1]['end'] -= 1
            #print "end tag: %s" % tag
            
class TianYa_Poster_HTML_Parser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.poster_div = None
        self.poster = False
        self.element = None
        self.detail = ''
        self.header_div = None
        self.uid = None
        self.famous = 0
        
    def unknown_starttag(self, tag, attrs):
        if tag == 'div':
            if len(attrs) > 0:
                for (key, value) in attrs:
                    if key == 'class' and value == 'atl-info' and not self.header_div:
                        self.header_div = 0
                    if key == 'class' and value[0:11] == 'bbs-content' and not self.poster_div:
                        self.poster_div = 0
                        self.element = {}
                     
            if self.header_div >= 0:
                self.header_div += 1
            elif self.poster_div >= 0:
                self.poster_div += 1
        
        if self.header_div >= 0 and tag == 'a':
            if len(attrs) > 0:
                for (key, value) in attrs:
                    if not self.uid and key == 'uid':
                        self.uid = value
                    if key == 'class' and value.find('star'):
                        self.famous = 1
                        
    def handle_data(self, data):
        if self.header_div > 0:
            self.detail += data
            
        if self.poster_div > 0:
            #print "end: %d, data: %s"  % (self.links[-1]['end'], data)
            if 'content' in self.element:
                self.element['content'] += data
            else:
                self.element['content'] = data
    
    def unknown_endtag(self, tag):
        if tag == 'div':
            if self.header_div > 0:
                self.header_div -= 1
                if self.header_div == 0:
                    self.header_div = -1
            elif self.poster_div > 0:
                self.poster_div -= 1
                if self.poster_div == 0:
                    self.poster_div = -1
            

class TianYa_Comment_HTML_Parser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.links = []
        self.comment = False
        
    def unknown_starttag(self, tag, attrs):
        if tag == 'div':
            if len(attrs) > 0:
                for (key, value) in attrs:
                    if key == 'class' and value == 'atl-item':
                        element = {'end':0}
                        self.links.append(element)
                        self.comment = True
                        
            if self.links and self.comment:
                self.links[-1]['end'] += 1
            
        if tag == 'a' and self.links and self.links[-1]['end'] > 0:
            if len(attrs) > 0:
                for (key, value) in attrs:
                    if key == 'uid':
                        self.links[-1]['uid'] = value
                        
    def handle_data(self, data):
        if self.links and self.links[-1]['end']>0:
            #print "end: %d, data: %s"  % (self.links[-1]['end'], data)
            if 'content' in self.links[-1]:
                self.links[-1]['content'] += data
            else:
                self.links[-1]['content'] = data
    
    def unknown_endtag(self, tag):
        if self.comment and tag == 'div':
            self.links[-1]['end'] -= 1
            if self.links[-1]['end'] == 0:
                self.comment = False
