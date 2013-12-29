#!/usr/local/bin/python
#encoding=utf8

import os,sys
from sets import Set
from numpy import *
from gensim import corpora, models, similarities
import segment
from idf import idf

class Topic(object):
    
    def __init__(self, keyword):
        self.keyword = keyword
        self.dictionary = None
        self.corpus = None
        self.tfidf = None 
        self.corpus_tfidf = None
        self.lsi = None
        self.index = None
        self.init_topics = 50
        self.init_topic_top_words = 50
        self.topic_distance = 0.2
        self.init_topic_keyword_rate = 0.5
        
    def init_document(self, document_list):
        init_document = [segment.top_words(document, self.keyword) for document in document_list]
        #i = 0
        #for document in init_document:
        #    print "document:%s, keywords:%s" % (document_list[i], " ".join(document))
        #    i += 1
        #sys.exit()
        self.dictionary = corpora.Dictionary(init_document)
        self.corpus = [self.dictionary.doc2bow(words) for words in init_document]
        self.tfidf = models.TfidfModel(self.corpus)
        self.corpus_tfidf = self.tfidf[self.corpus]
        
        self.lsi = models.LsiModel(self.corpus_tfidf, num_topics=self.init_topics, id2word=self.dictionary)
        #self.lsi = models.LsiModel(self.corpus, num_topics=self.init_topics, id2word=self.dictionary)
        #i = 0
        #for l in self.lsi[self.corpus_tfidf]:
        #    print "index: %d, corpus: %s" % (i, l)
        #    i += 1
        #for t in self.lsi.print_topics(20, 100):
        #    print "topic: %s" % t
        #sys.exit()
        self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])
        topics_list = self.lsi.get_topics(self.init_topics, self.init_topic_top_words)
        topics_list = self.extract_topic_keyword(topics_list)
        topic_info = self.recurse_topic(topics_list)
        
        for index, topic in enumerate(topic_info):
            sorted_topic_word = sorted(topic['word'].items(), key=lambda k:k[1], reverse=True)
            for p, word in sorted_topic_word:
                print "word:%s, p:%s" % (word, p)
            print "topic #%d, words:%s, document count:%d" % (index, " ".join(topic['word'].keys()), len(topic['document']))
            for i in topic['document']:
                print document_list[i]
                
        
    def add_document(self, document_list):
        pass
    
    def extract_topic_keyword(self, topic_list):
        new_topic_list = []
        for topic in topic_list:
            base_p = float(topic[0][0])
            new_topic = []
            for p, word in topic:
                if abs(float(p)/base_p) >= self.init_topic_keyword_rate:
                    new_topic.append([p, word])
            new_topic_list.append(new_topic)
        return new_topic_list
    
    def recurse_topic(self, topic_list):
        all_word_set = Set([])
        all_word_list = []
        id2words = []
        words2id = {}
        for topic in topic_list:
            #print "new topic********************"
            for p, word in topic:
                #print "%s, %s" % (p, word)
                all_word_list.append(word)
                if word not in all_word_set:
                    all_word_set.add(word)
                    id2words.append(word)
                    words2id[word] = len(id2words)-1
                 
        topics_vector = []   
        for topic in topic_list:
            topic_vector = [0]*len(all_word_set)
            for p, word in topic:
                 #if word in idf.idf:
                 #    word_tf_idf = log(float(TOTAL_DOCUMENT)/float(document_fre[word]))
                 #else:
                 #    word_tf_idf = log(float(TOTAL_DOCUMENT))
                 vector_value = abs(p)
                 #*log(float(TOTAL_DOCUMENT)/float(document_fre[word]))
                 topic_vector[words2id[word]] = vector_value
            topics_vector.append(topic_vector)
        #print topics_vector
        topics_matrix = array(topics_vector)
        topic_vsm = dot(topics_matrix,topics_matrix.transpose())
        index = 0
        merged_topic = []
        for element in topic_vsm:
            tid_set = None
            if len(merged_topic) > 0:
                for mt in merged_topic:
                    if index in mt:
                        if tid_set:
                            tid_set |= mt
                            merged_topic.remove(mt)
                        else:
                            tid_set = mt
            if not tid_set:
                tid_set = Set([])
                tid_set.add(index)
                merged_topic.append(tid_set)
                       
            base_vsm = element[index]
            for tid, vsm in enumerate(element[(index+1):]):
                if vsm/base_vsm > self.topic_distance:
                    tid_set.add(tid+index+1)
            
            index += 1
        
        topic_info = []
        topic_map = {}
        for mt in merged_topic:
            topic = {}
            topic['topic'] = list(mt)
            topic_info.append(topic)
            for t in list(mt):
                topic_map[t] = len(topic_info)-1
            
        index = 0
        for topic in topic_list:
            tid = topic_map[index]
            if 'word' not in topic_info[tid]:
                topic_info[tid]['word'] = {}
            #print tid, topic_info[tid]['word']
            for p, word in topic:
                #if word in document_fre:
                #    word_tf_idf = log(float(TOTAL_DOCUMENT)/float(document_fre[word]))
                #else:
                #    word_tf_idf = log(float(TOTAL_DOCUMENT))
                if word in topic_info[tid]['word']:
                    topic_info[tid]['word'][word] += abs(p)*idf[word]
                else:
                    topic_info[tid]['word'][word] = abs(p)*idf[word]
            index += 1
        
        index = 0
        for document in self.lsi[self.corpus_tfidf]:
            if len(document) <= 0:
                index += 1
                continue
            sorted_document = sorted(document, key=lambda k:abs(k[1]), reverse=True)
            topic_id = sorted_document[0][0]
            tid = topic_map[topic_id]
            #print tid
            if 'document' in topic_info[tid]:
                topic_info[tid]['document'].append(index)
            else:
                topic_info[tid]['document'] = []
                topic_info[tid]['document'].append(index)
            index += 1
            
        #for index, topic in enumerate(topic_info):
        #    if 'document' in topic:
        #        document_length = len(topic['document'])
        #        pos_list = [document_sentiment[document][1] for document in topic['document'] if document_sentiment[document][0] == 'pos']
        #        neg_list = [document_sentiment[document][1] for document in topic['document'] if document_sentiment[document][0] == 'neg']
        #    else:
         #       document_length = pos_length = neg_length = 0 
            
          #  print "topic #%d, words:%s, document count:%d, positive document number:%d, point: %f, negative document number:%d, point: %f" % (index, " ".join(topic['word'].keys()), document_length, len(pos_list), sum(pos_list)/len(pos_list), len(neg_list), sum(neg_list)/len(neg_list))
            #print "topic #%d, words:%s" % (index, " ".join(topic['word'].keys()))
            
        return topic_info