#!/usr/local/bin/python
#encoding=utf8

import os
import marshal

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'idf.marshal')
idf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'idf.txt')

#default_idf = 17.911552
default_idf = 1

class idf_info(object):
    
    def __init__(self):
        self.fname = data_path if os.path.isfile(data_path) else idf_path
        self.load()

    def save(self):
        marshal.dump(self.idf, open(data_path, 'wb'))

    def load(self):
        if self.fname.find('marshal') != -1:
            self.idf = marshal.load(open(self.fname, 'rb'))
            return 
        self.idf = {}
        with open(self.fname) as fp:
            for line in fp.readlines():
                word, freq = line.strip(" \n").split(" ")
                self.idf[word] = float(freq)
                
    def __getitem__(self, word):
        return self.idf[word] if word in self.idf else default_idf
    
    def get_idf(self, word):
        return self.idf[word] if word in self.idf else default_idf
                
    #def __del__(self):
        #self.save()

#idf = idf_info()
       
#if __name__ == "__main__":
#    idf = idf()
#    print idf['朱元璋']    
#    del idf
    