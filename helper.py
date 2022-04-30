
import pandas as pd
import numpy as np
import re
import string
from nltk.corpus import stopwords
from urlextract import URLExtract
from collections import Counter
import emoji

stop_w_hin=pd.read_csv('hindi-stop-words.csv')
stop_w_eng=pd.read_csv('stop-word.csv')


##Data making useful 
def prepare_data(data):
    time=re.findall('\d*/\d*/\d*,\s+\d*:\d*\s+[A|P|a|p][M|m]\s+',data)
    msg=re.split('\d*/\d*/\d*,\s+\d*:\d*\s+[A|P|a|p][M|m]\s+-\s+',data)[1:]
    
    chat=pd.DataFrame({
    'time':time,
    "msg":msg
    })
    chat['sender']=chat.msg.apply(reg)     
    chat['msg']=chat.msg.apply(split)
    chat['msg']=chat.msg.str.replace(r'(\n)$','',regex=True)
    chat.time=pd.to_datetime(chat.time) 
    chat['day']=chat.time.dt.day
    chat['month']=chat.time.dt.month_name()
    chat['year']=chat.time.dt.year
    chat['hour']=chat.time.dt.hour
    chat['minute']=chat.time.dt.minute
    return chat 
##split for remove sender from msg columns 
def split(x):
        l=re.split(':',x,1)
        if len(l)>1:
            return l[1]
        else:
            return l[0]

## find sender from msg columns
def reg(x):
    l=re.split(':',x)
    if len(l)>1:
        return l[0]
    else:
        return 'group'

## find unique user in data
def unique_user_list(data):
    users_list=data.sender.unique().tolist()
    users_list.sort()
    users_list.insert(0,'overall')
    return users_list
   
def selected_data_table(data,selected_name):
    if selected_name=='overall':
        return data
    else:
        data=data[data.sender==selected_name]
        return data

##word count

def word_count(data):
    total=data.msg.apply(lambda x: len(x.split(' '))-1)
    return sum(total)

def media_count(data):
    total=sum(data.msg.apply(lambda x: len(re.findall('( <Media omitted>| <media omitted>)',x))))
    return total

def link_count(data):
    url_obj=URLExtract()
    total=sum(data.msg.apply(lambda x: len(url_obj.find_urls(x))))
    return total

#for most busy user
def most_busy_user(data):
    values=data.sender.value_counts().head(5)
    return values

#for 
def most_busy_user_data_frame(data):
    data_frame=round(data.sender.value_counts()/data.shape[0]*100).reset_index()
    return data_frame.rename(columns={'index':'sender',"sender":'%'})

# for most comman word 
def count_word(data,selected_type):
    if selected_type!='overall':
        data=data[data.sender==selected_type]
    data=data[data.sender!='group']
    data=data[data.msg!=' <Media omitted>']
    data.msg=data.msg.apply(lambda x:x.lower())
    index_for_delete=data[(data.msg.str.contains('.*[(][Ff][a-zA-Z\s]*[)]')) | (data.msg.str.contains('http'))].index[:]
    data.drop(index_for_delete,axis=0,inplace=True)
    data.msg=data.msg.apply(remove_number)
    data.msg=data.msg.apply(remove_puctuation)
    data.msg=data.msg.apply(stop_word_eng)
    data.msg=data.msg.apply(stop_word_hin)
    if len(data)<1:
        return 'empty'
    word_occur=[]
    for i in data.msg:
        word_occur.extend(i.split())
    data=Counter(word_occur).most_common(20)
    data=pd.DataFrame(data)
    data=data.rename(columns={0:'word',1:'occur'})
    data.occur=data.occur.astype('str')
    return data



# for stop word remover series


def combine(data):
    c=[]
    for i in data:
        c.extend(i)
    return c


def stop_word_eng(data):
    word=[]
    for i in data.split():
        if i not in combine(stop_w_eng.values):
            word.append(i)
    return " ".join(word)

def stop_word_hin(data):
    word=[]
    for i in data.split():
        if i not in combine(stop_w_hin.values):
            word.append(i)
    return " ".join(word)


#for remove punctuation from series
def remove_puctuation(data):
    punctuations=string.punctuation
    for i in punctuations:
        if i in data:   
            data=data.replace(i,'')
    return data
#for remove number form series
def remove_number(data):
    for i in range(10):
        if str(i) in data:
           data=data.replace(str(i),'')
            
    return data

#most commen emoji used
def emoji_count(data):
    emoji_collector=[]
    for i in data.msg:
        for j in i:
            if j in emoji.UNICODE_EMOJI['en']:
                emoji_collector.extend(j)
    if len(emoji_collector)==0:
        return 'nothing'
    emoji_collector=Counter(emoji_collector).most_common(10)
    emoji_collector=pd.DataFrame(emoji_collector).rename(columns={0:'emoji',1:'occur'})
    return emoji_collector

#most chat on year

def most_chat_on_year_month(data):
    data=data.groupby(['year','month']).count()['msg'].reset_index()
    data['year-month']=data.year.apply(lambda x: str(x))+'-'+data.month
    return data[['year-month','msg']]

# #most msg send day wise
# def msg_day_wise(data):
#     data["date"]=data.time.dt.date
#     data=data.groupby('date').count()['msg']
#     return data

#active on weak
def week_active(data):
    data['day_name']=data.time.dt.day_name()
    return data.groupby('day_name').count()['msg'].reset_index().sort_values('msg',ascending=False)

#active on month
def month_active(data):
    return data.groupby('month').count()['msg'].reset_index().sort_values('msg',ascending=False)

def hour_active_on_week(data):
    data['day_name']=data.time.dt.day_name()
    data=data.groupby(['day_name','hour']).count()['msg'].reset_index()
    data=pd.pivot_table(data=data,index='day_name',columns='hour',values='msg')
    data=hour_colum_adder(data).fillna(0)
    return data

#hour colum adder
def hour_colum_adder(c):
    adder=pd.DataFrame()
    for i in range(0,24):
        if i in c.columns:
            adder[i]=c[i]
        else:
            adder[i]=np.nan
    adder.columns=list(range(1,25))
    return adder


#most busy day in month
def busy_day(data):
    data=data.groupby(['month','day']).count()['msg'].reset_index()
    data=pd.pivot_table(data=data,index='month',columns="day",values='msg')
    data=day_colum_adder(data).fillna(0)
    return data

#day column adder
def day_colum_adder(c):
    adder=pd.DataFrame()
    for i in range(1,32):
        if i in c.columns:
            adder[i]=c[i]
        else:
            adder[i]=np.nan
    adder.columns=list(range(1,32))
    return adder

#most  media share admin
def most_media(data):
    data=data[data.msg==' <Media omitted>']['sender'].value_counts().head(10).reset_index()
    data.rename(columns={'index':'sender','sender':'msg'},inplace=True)
    return data


#url sender admin

def url_sender(data):
    url_obj=URLExtract()
    data['url_num']=data.msg.apply(lambda x: len(url_obj.find_urls(x)))
    data=data[data.url_num>0]
    data=data.groupby(['sender']).sum()['url_num'].reset_index().sort_values('url_num',ascending=False).head(10)

    #data=data.sender.value_counts().reset_index().head(10)
    data.rename(columns={'index':'sender','url_num':'url'},inplace=True)
    return data
