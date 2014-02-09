#encoding=utf8
#from __future__ import unicode_literals

import sys
import os.path
import marshal
from math import log, exp

from util.frequency import AddOneProb

class Bayes(object):

    def __init__(self):
        self.d = {}
        self.total = 0

    def save(self, fname):
        d = {}
        d['total'] = self.total
        d['d'] = {}
        for k, v in self.d.items():
            d['d'][k] = v.__dict__
        #if sys.version_info.major == 3:
        #    fname = fname + '.3'
        marshal.dump(d, open(fname, 'wb'))

    def load(self, fname):
        #if sys.version_info.major == 3:
        #    fname = fname + '.3'
        if not os.path.isfile(fname):
            return 
        d = marshal.load(open(fname, 'rb'))
        self.total = d['total']
        self.d = {}
        for k, v in d['d'].items():
            self.d[k] = AddOneProb()
            self.d[k].__dict__ = v

    def train(self, data):
        for d in data:
            c = d[1]
            if c not in self.d:
                self.d[c] = AddOneProb()
            for word in d[0]:
                self.d[c].add(word, 1)
        self.total = sum(map(lambda x: self.d[x].getsum(), self.d.keys()))

    def classify(self, x):
        tmp = {}
        for k in self.d:
            tmp[k] = 0
            print k
            for word in x:
                print word, self.d[k].freq(word)
                #tmp[k] += log(self.d[k].getsum()) - log(self.total) + log(self.d[k].freq(word))
                tmp[k] += log(self.d[k].freq(word))
            #print k, tmp[k], " ".join(x)
        sys.exit()
        ret, prob = 0, 0
        for k in self.d:
            now = 0
            for otherk in self.d:
                value = tmp[otherk]-tmp[k] if tmp[otherk]-tmp[k] < 100 else 100
                #print value
                now += exp(value)
            #print k, now
            now = 1/now
            if now > prob:
                ret, prob = k, now
        return (ret, prob)

class Spam_Bayes(object):

    def __init__(self):
        self.d = {}
        self.total = 0

    def save(self, fname):
        d = {}
        d['total'] = self.total
        d['d'] = {}
        for k, v in self.d.items():
            d['d'][k] = v.__dict__
        #if sys.version_info.major == 3:
        #    fname = fname + '.3'
        marshal.dump(d, open(fname, 'wb'))

    def load(self, fname):
        #if sys.version_info.major == 3:
        #    fname = fname + '.3'
        if not os.path.isfile(fname):
            return 
        d = marshal.load(open(fname, 'rb'))
        self.total = d['total']
        self.d = {}
        for k, v in d['d'].items():
            self.d[k] = AddOneProb()
            self.d[k].__dict__ = v

    def train(self, data):
        for d in data:
            c = d[1]
            if c not in self.d:
                self.d[c] = AddOneProb()
            for word in d[0]:
                self.d[c].add(word, 1)
        self.total = sum(map(lambda x: self.d[x].getsum(), self.d.keys()))

    def classify(self, x):
        tmp = {}
        for k in self.d:
            tmp[k] = 0
            for word in x:
                tmp[k] += log(self.d[k].getsum()) - log(self.total) + log(self.d[k].freq(word))
                    
        ret, prob = 0, 0
        for k in self.d:
            now = 0
            for otherk in self.d:
                now += exp(tmp[otherk]-tmp[k])
            now = 1/now
            if now > prob:
                ret, prob = k, now
        return (ret, prob)
