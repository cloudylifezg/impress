#encoding=utf8

import sys
import os.path
import marshal
from math import log, exp

data_marsha_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop_words.marshal')
data_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop_words.txt')

class StopWord_Filter(object):
    def __init__(self):
        self.stopwords = set()
        self.file_name = data_marsha_path if os.path.isfile(data_marsha_path) else data_file_path
        self.cache = True
        self.load()
        
    def load(self):
        if self.file_name.find('marshal') != -1:
            self.stopwords = marshal.load(open(self.file_name, 'rb'))
            return 
        self.cache = False
        fp = open(self.file_name, 'r')
        for word in fp.readlines(): 
            self.stopwords.add(word.strip())
        fp.close()

    def save(self):
        marshal.dump(self.stopwords, open(data_marsha_path, 'wb'))
        
    def filter(self, words):
        return [word for word in words if word not in self.stopwords]

    def __del__(self):
        #if not self.cache:
        #    self.save()
        pass
    
