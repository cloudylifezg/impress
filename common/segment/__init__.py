#encoding=utf8

import re,sys
import jieba
from jieba import posseg,analyse
from util import stopwords_filter, language
from idf import idf

hanzi_re = re.compile("[\u4e00-\u9fa5]+")
swfilter = stopwords_filter.StopWord_Filter()

word_feature = {'n':'名词', 'nr':'人名', 'ns':'地名', 'nt':'机构团体名', 'nz':'其他专用名词', 'ng':'名词性语>素', 
                't':'时间词', 'tg':'时间词性语素',
                's':'处所词',
                'f':'方位词',
                'v':'动词', 'vd':'副动词', 'vshi':'动词是', 'vyou':'动词有', 'vf':'趋向动词', 'vx':'形式动词', 'vi':'不及物动词', 'vl':'动词性惯用语', 'vg':'动词性语素',
                'a':'形容词', 'ad':'副形词', 'an':'名形词', 'ag':'形容词性语素', 'al':'形容词性惯用语',
                'b':'区别词', 'bl':'区别词性惯用语',
                'z':'状态词',
                'r':'代词', 'rg':'代词性语素',
                'm':'数词', 'mq':'数量词',
                'd':'副词',
                'p':'介词',
                'c':'连词',
                'u':'助词',
                'e':'叹词',
                'y':'语气词',
                'o':'拟声词',
                'h':'前缀',
                'k':'后缀',
                'x':'字符串',                                                                                
                'w':'标点符号',
                }

word_feature['keyword_omit'] = set(['b', 'z', 'r', 'm', 'd', 'p', 'c', 'u', 'e', 'y', 'o', 'h', 'k', 'w'])

TOP_WORD_RATE = 1.00
TOP_WORD_NUM = 20

def seg(text, cut_all=False):
    text = language.transfer(text)
    return jieba.cut(text, cut_all)

def posseg(text):
    text = language.transfer(text)
    return jieba.posseg(text)

def seg_mean_words(text, keyword):
    #words =  [w.word.strip() for w in jieba.posseg.cut(text) if w.word.strip()!="" and w.flag.lower()[0] not in word_feature['keyword_omit']]
    words = []
    for w in jieba.posseg.cut(text):
        #关键词词性不对
        if w.word.strip() == keyword.word:
            if w.flag.lower()[0] not in keyword.flag:
                return None
            else:
                continue
        if w.flag.lower()[0] not in word_feature['keyword_omit'] and len(w.word.strip())>1 and not swfilter.stop_word(w.word.strip()):
            words.append(w.word.strip())
        
    return words

def top_words(text, keyword, top_num=0, top_rate=TOP_WORD_RATE):
    word_list = seg_mean_words(text, keyword)
    if not word_list:
        return []
    weight_words = {}
    for word in word_list:
        if word in weight_words:
            continue
        weight_words[word] = float(word_list.count(word))/len(word_list) * idf[word]
            
    sorted_words = sorted(weight_words.items(), key=lambda k:k[1], reverse=True)
    if top_num > 0:
        return [w[0] for w in sorted_words][0:top_num]
    top_words = int(round(len(word_list)*top_rate))
    return [w[0] for w in sorted_words][0:top_words]

def extract_tags(text, top_num=20):
    return jieba.analyse.extract_tags(text, top_num)