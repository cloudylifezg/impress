#encoding=utf8
#from __future__ import unicode_literals

import os,sys
import segment
from util import stopwords_filter
from classifier.bayes import Bayes

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentiment.marshal')
buaa_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buaa_sentiment.marshal')

negative_sentence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'negative_sentence.txt')
negative_word_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'negative_words.txt')
positive_sentence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'positive_sentence.txt')
positive_word_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'positive_words.txt')

buaa_angry_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_0.1_1.txt')
buaa_hate_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_0.1_2.txt')
buaa_happy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_0.1_3.txt')
buaa_sad_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_0.1_4.txt')

#swfilter = stopwords_filter.StopWord_Filter()

class Sentiment(object):

    def __init__(self):
        self.classifier = Bayes()

    def save(self, fname=data_path):
        self.classifier.save(fname)

    def load(self, fname=data_path):
        self.classifier.load(fname)
        if self.classifier.total == 0:
            file_list = [(negative_sentence_path,positive_sentence_path), (negative_word_path,positive_word_path)]
            self.init(file_list)
    
    def buaa_save(self, fname=buaa_data_path):
        self.classifier.save(fname)
    
    def buaa_load(self, fname=buaa_data_path):
        self.classifier.load(fname)
        if self.classifier.total == 0:
            file_list = [(buaa_angry_path,buaa_hate_path, buaa_happy_path, buaa_sad_path)]
            self.buaa_init(file_list)
        
    def init(self, file_list):
        for file in file_list:
            self.train(open(file[0], 'r').readlines(), open(file[1], 'r').readlines())
            
    def buaa_init(self, file_list):
        for file in file_list:
            self.buaa_train(open(file[0], 'r').readlines(), open(file[1], 'r').readlines(), open(file[2], 'r').readlines(), open(file[3], 'r').readlines())

    def handle(self, doc):
        words = segment.seg(doc)
        #words = swfilter.filter(list(words))
        return list(words)

    def train(self, neg_docs, pos_docs):
        data = []
        for sent in neg_docs:
            data.append([self.handle(sent), 'neg'])
        for sent in pos_docs:
            data.append([self.handle(sent), 'pos'])
        self.classifier.train(data)
        
    #情感更加丰富：愤怒， 厌恶， 高兴， 低落
    def buaa_train(self, angry_docs, hate_docs, happy_docs, sad_docs):
        data = []
        for sent in angry_docs:
            data.append([self.handle(sent.decode('utf8')), 'angry'])
        for sent in hate_docs:
            data.append([self.handle(sent.decode('utf8')), 'hate'])
        for sent in happy_docs:
            data.append([self.handle(sent.decode('utf8')), 'happy'])
        for sent in sad_docs:
            data.append([self.handle(sent.decode('utf8')), 'sad'])
        self.classifier.train(data)

    def classify(self, sent):
        ret, prob = self.classifier.classify(self.handle(sent))
#        if ret == 'pos':
#            return prob
#        return 1-prob
        return (ret, prob)
    
    def __del__(self):
        self.buaa_save()
        
classifier = Sentiment()
#classifier.load()
classifier.buaa_load()

def classify(sent):
    return classifier.classify(sent)



