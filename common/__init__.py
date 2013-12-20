#encoding=utf8

import sys
from summary.textrank import TextRank
from util import sentence, stopwords_filter
import sentiment
import segment

swfilter = stopwords_filter.StopWord_Filter()

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
    print sentiment.classify("林志颖卖“爱碧丽”，方舟子打假，大家很关注，@我们的也很多。经现场检查，位于上海松江、具有生产许可证的“上海葡萄王企业有限公司”与“爱碧丽”签订了商标使用许可合同，“爱碧丽”系列中的胶原蛋白饮料，都是它生产的普通食品。产品本身无害，但普通食品不应宣传美容功效。")
    
