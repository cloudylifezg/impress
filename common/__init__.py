#!/usr/local/bin/python
#encoding=utf8

import sys
import math

from topic import topic
from util import language
import sentiment 
import segment
import jieba

def f(text):
    sentences = sentence.get_sentences(text)
    doc = []
    for sent in sentences:
        #print "%s" % sent.encode('utf8')
        words = segment.seg(sent)
        words = swfilter.filter(words)
        doc.append(words)
    rank = TextRank(doc)
    rank.solve()                                                                               
    ret = []
    for index in rank.top_index(limit=5):
        ret.append(sentences[index].strip())

if __name__ == '__main__':
    kword = segment.st_keyword(u'永城', set(['n', 'z']))
    topic = topic.Topic(kword)
    fp = open('/Users/zhanggui/nltk_learn/train_data/weibo.dat', 'rb')
    #fp = open('/Users/zhanggui/source/impress/common/sentiment/negative_sentence.txt', 'r')
    #fp = open('/Users/zhanggui/source/impress/common/sentiment/sample_0.1_5.txt', 'r')
    text = fp.read().rstrip().decode('utf-8').split('\n')
    document = []
    for text_str in text:
        #text_str = t.split('    ')[2]
        pos = text_str.find('：'.decode('utf-8'))
        if pos != -1:
            text_str = text_str[(pos+1):]
        text_str = language.transfer(text_str)
        document.append(text_str)
    i = 0
    #for doc in document:
    #    print doc
    #    i += 1
    #    print(sentiment.classify(doc))
    #    if i > 50:
    #        sys.exit()
    topic.init_document(document)


