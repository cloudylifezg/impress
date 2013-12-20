#encoding=utf8

import os.path
import math
import marshal

data_marsha_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dict_frequence.marshal')
data_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dict_frequence.txt')

class BM25(object):
    def __init__(self, docs):
        self.D = len(docs)
        self.avgdl = sum(map(lambda x: len(x)+0.0, docs)) / self.D
        self.docs = docs
        self.f = []
        self.df = {}
        self.idf = {}
        self.k1 = 1.5
        self.b = 0.75
        self.L = 500000
        self.word_idf = {}
        self.file_name = data_marsha_path if os.path.isfile(data_marsha_path) else data_file_path
        self.load()
        self.init()
        self.save()
        
    def load(self):
        if self.file_name.find('marshal') != -1:
            self.word_idf = marshal.load(open(self.file_name, 'rb'))
            return 
        fp = open(self.file_name, 'r')
        for line in fp.readlines():
            parts = line.strip().split(" ")
            if len(parts) > 2:
                self.word_idf[parts[0].strip()] = int(parts[1].strip())
        fp.close()

    def save(self):
        marshal.dump(self.word_idf, open(data_marsha_path, 'wb'))

    def init(self):
        for doc in self.docs:
            tmp = {}
            for word in doc:
                if not word in tmp:
                    tmp[word] = 0
                tmp[word] += 1
                if not word in self.word_idf:
                    self.word_idf[word] = 0
                self.word_idf[word] += 1
            self.f.append(tmp)
            for k, v in tmp.items():
                if k not in self.df:
                    self.df[k] = 0
                self.df[k] += 1
        for k, v in self.df.items():
            self.idf[k] = math.log(self.L-self.word_idf[k]+0.5)-math.log(self.word_idf[k]+0.5)

    def sim(self, doc, index):
        score = 0
        for word in doc:
            if word not in self.f[index]:
                continue
            score += (self.idf[word]*self.f[index][word]*(self.k1+1)
                      / (self.f[index][word]+self.k1*(1-self.b+self.b*self.D
                                                      / self.avgdl)))
        return score

    def simall(self, doc):
        scores = []
        for index in range(self.D):
            score = self.sim(doc, index)
            scores.append(score)
        return scores
    
    def __del__(self):
        self.save()
        
#if __name__ == "__main__":
#    bm = BM25([[u'语言', u'自然', u'计算机'],[u'测试', '相似']])
#    del bm
