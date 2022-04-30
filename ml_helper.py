from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
import re
import string
import nltk
from nltk.corpus import stopwords
from urlextract import URLExtract
from collections import Counter
import emoji
from helper import stop_word_hin
from helper import stop_word_eng
from helper import remove_puctuation
from helper import remove_number
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity

#tokenizer

pt=PorterStemmer()


def tokenize(data):
    d=nltk.word_tokenize(data)
    d=" ".join(d)
    return d

def porter(data):
    d=[]
    for i in data.split():
        d.append(pt.stem(i))
    d=" ".join(d)
    return d


def sililar_admin(data):
    data=data[data.sender!='group']
    data=data[data.msg!=' <Media omitted>']
    data.msg=data.msg.apply(lambda x:x.lower())
    index_for_delete=data[(data.msg.str.contains('.*[(][Ff][a-zA-Z\s]*[)]')) | (data.msg.str.contains('http'))].index[:]
    data.drop(index_for_delete,axis=0,inplace=True)
    data.msg=data.msg.apply(lambda x: emoji.demojize(x))
    data.msg=data.msg.apply(remove_number)
    data.msg=data.msg.apply(remove_puctuation)
    data.msg=data.msg.apply(stop_word_eng)
    data.msg=data.msg.apply(stop_word_hin)
    data.msg=data.msg.apply(tokenize)
    data.msg=data.msg.apply(porter)
    return data
    
#adding msg 
def add_string(data):
    unique=data.sender.unique()
    ms=pd.DataFrame()
    for i in unique:
        data2=data[data.sender==i]
        another=[]
        for j in data2.msg:
            for  k in j.split():
                another.append(k)
        another=" ".join(another)   
        e=pd.Series(another)
        ms=pd.concat([ms,e],axis=0)
    ms.index=range(0,len(ms))
    ms=pd.concat([pd.Series(data.sender.unique()),ms],axis=1)
    ms.columns=['sender','msg']      
    return ms 


#appply ML process

def Sklearn(data):
    #apply vectorization
    cv=CountVectorizer(max_features=3000)
    k_dis=cv.fit_transform(data.msg).toarray()
    feature=cv.get_feature_names()
    
    #cosine distance
    cs=cosine_similarity(k_dis)
    cs_data=pd.DataFrame(cs)
    cs_data.columns=data.sender
    cs_data.index=data.sender
    return cs_data

def adding_all_functio(data):
    data=sililar_admin(data)
    data=add_string(data)
    data=Sklearn(data)
    return data

#siliear user selecting

def select_similar_user(data,selected):
    user_list=data.sort_values(selected,ascending=False)[selected].index[1:6]
    user_list=pd.DataFrame(user_list)
    return user_list