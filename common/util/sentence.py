#encoding=utf8

delimiter = ',.!?:;~，。！？：；'.decode('utf8')  

def get_sentences(doc):
    doc = doc.decode('utf8')
    start = 0
    i = 0  #记录每个字符的位置
    sents = []
    punt_list = delimiter
    for word in doc:
        if word in punt_list:
            sents.append(doc[start:i+1].strip(delimiter))
            start = i + 1  
            i += 1
        else:
            i += 1  
    if start < len(doc):
        sents.append(doc[start:].strip()) 
    return sents
