import pandas as pd
import numpy as np
import streamlit as st
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import ml_helper


uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
     bytes_data = uploaded_file.getvalue()
     data=bytes_data.decode('utf-8')
     data=helper.prepare_data(data)
     #st.table(data)




rad=st.sidebar.radio('select operation',('Analysis','similar member'))


if rad=='Analysis':
    
    
    selected=st.sidebar.selectbox('select member',helper.unique_user_list(data))
    data_=helper.selected_data_table(data,selected)
    button_value=st.sidebar.button('select user type')
    if button_value:
        #Data Table of User
        st.header(f"Data Table of {selected}")
        st.dataframe(helper.selected_data_table(data,selected))
        st.header('Top Statistics')
        col1,col2,col3,col4=st.columns(4)
        with col1:
            st.header('Total Message')
            st.header(data_.shape[0])
        with col2:
            st.header('Total words')
            st.header(helper.word_count(data_))
        with col3:  
            st.header('Total Media')
            st.header(helper.media_count(data_))
        with col4:
            st.header('Total Links')
            st.header(helper.link_count(data_))

        #for overall only 
        if selected=='overall':
            
            
            col1,col2=st.columns(2)
            fig,pl=plt.subplots()
            values=helper.most_busy_user(data)

            with col1:
                st.header('Most active user')
                pl.bar(values.index,values.values,color='green')
                plt.xticks(rotation=90)
                st.pyplot(fig)
            with col2:
                st.header('contribution in %')
                data_frame=helper.most_busy_user_data_frame(data)
                st.dataframe(data_frame)
        
        #media sender analysis
        st.header('Media')
        col1,col2=st.columns(2)
        most_send_media_list=helper.most_media(data_)
        with col1:
            st.header(f'Media Sended by {selected}')
            st.dataframe(most_send_media_list)
        with col2:
            st.header('bar graph')
            fig,pl=plt.subplots()
            pl.bar(most_send_media_list.sender,most_send_media_list.msg)
            plt.xticks(rotation=70)
            st.pyplot(fig)

        st.header('URL ')
        col1,col2=st.columns(2)
        media_sender=helper.url_sender(data_)
        with col1:
            st.header(f'URL sended by {selected}')
            st.dataframe(media_sender)
        with col2:
            st.header('bar graph')
            fig,pl=plt.subplots()
            pl.bar(media_sender.sender,media_sender.url)
            plt.xticks(rotation=70)
            st.pyplot(fig) 



        #most common word 
        st.header('Words ')
        d=helper.count_word(data,selected)

        if selected!='group' and type(d)!=str:
            
            col1,col2=st.columns(2)
            with col1:
                st.header('most common word table')
                st.dataframe(d)
            
            with col2:
                st.header('bar graph ')
                fig1,v=plt.subplots()
                v.barh(d.word,d.occur)
                plt.xticks(rotation='vertical')
                st.pyplot(fig1)
        else :
            st.text('sorry we were thinking this is not usefull...... beacase this is group or sender nothing sended')
        
        #for emojis
        st.header('Emojis ')
        st.header('Most used emojis')
        emoji_list=helper.emoji_count(data_)
        if type(emoji_list)!=str:
            col1,col2=st.columns(2)
            with col1:
                st.dataframe(emoji_list)
            with col2:
                fig,pl=plt.subplots()
                pl.bar(emoji_list.emoji,emoji_list.occur,color='red')
                st.pyplot(fig)
        else:
            st.text(f'Nothing emoji sended by {selected}')

        #most chat on year and month wise
        st.header('Most Chat On Year-Month')
        most_chat_year_month=helper.most_chat_on_year_month(data_)
        fig,pt=plt.subplots()
        pt.plot(most_chat_year_month.iloc[:,0],most_chat_year_month.iloc[:,1],color='c')
        plt.xticks(rotation=90)
        plt.xlabel('year-month')
        plt.ylabel('msg number')
        st.pyplot(fig)



        #most active on week
        st.header('Most Active week')
        active_day=helper.week_active(data_)
        fig,pt=plt.subplots()
        pt.bar(active_day.day_name,active_day.msg,color='c')
        plt.xticks(rotation=70)
        st.pyplot(fig)

        #most active on month
        st.header('Most Active Month')
        active_month=helper.month_active(data_)
        fig,pt=plt.subplots()
        pt.bar(active_month.month,active_month.msg,color='c')
        plt.xticks(rotation=70)
        st.pyplot(fig)    

        #most active hour on week
        st.header('Most Active Hour On Week')
        active_hour=helper.hour_active_on_week(data_)
        st.dataframe(active_hour)
        fig=plt.figure(figsize=(12,8))
        sns.heatmap(active_hour,cmap="YlGnBu")
        plt.ylabel('Week')
        plt.xlabel('Hours ( 1 means 0-1)')
        st.pyplot(fig)


        #most busy day
        st.header('Busy Day')
        busy_d=helper.busy_day(data_)
        fig=plt.figure(figsize=(12,8))
        sns.heatmap(busy_d)
        st.pyplot(fig)


    #ML releated code

if rad=="similar member":
    if len(data.sender.unique())>3:
        st.sidebar.header('Similar User')
        data=ml_helper.adding_all_functio(data)
        selected=data.columns
        select=st.selectbox('select user',selected)
        list=ml_helper.select_similar_user(data,select)
        for  i in range(len(list)):
            st.header(list.iloc[i].sender)
       

        