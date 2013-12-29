#encoding=utf8
#from __future__ import unicode_literals

import os
import segment
from util import stopwords_filter
from classifier.bayes import Spam_Bayes

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comment_spam.marshal')

negative_comment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'negative_comment.txt')
positive_comment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'positive_comment.txt')

swfilter = stopwords_filter.StopWord_Filter()

class AntiSpam(object):

    def __init__(self):
        self.classifier = Spam_Bayes()

    def save(self, fname=data_path):
        self.classifier.save(fname)

    def load(self, fname=data_path):
        self.classifier.load(fname)
        if self.classifier.total == 0:
            file_list = [(negative_comment_path,positive_comment_path)]
            self.init(file_list)
        
    def init(self, file_list):
        for file in file_list:
            self.train(open(file[0], 'r').readlines(), open(file[1], 'r').readlines())

    def handle(self, doc):
        words = segment.seg(doc)
        words = swfilter.filter(words)
        return words

    def train(self, neg_docs, pos_docs):
        data = []
        for sent in neg_docs:
            data.append([self.handle(sent), 'ham'])
        for sent in pos_docs:
            data.append([self.handle(sent), 'spam'])
        self.classifier.train(data)

    def classify(self, sent):
        ret, prob = self.classifier.classify(self.handle(sent))
#        if ret == 'pos':
#            return prob
#        return 1-prob
        return (ret, prob)
    
    def __del__(self):
        self.save()

classifier = AntiSpam()
classifier.load()

def AntiSpam(sent):
    return classifier.classify(sent)