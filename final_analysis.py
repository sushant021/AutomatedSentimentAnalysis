# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 21:53:32 2019

@author: nsush
"""

import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd

#mongo client
client = MongoClient('mongodb+srv://sushant_021:pass123@cluster0-rosmg.mongodb.net/test?retryWrites=true&w=majority')

# knowledge base 
db = client.FinalAssignmentData
knowledge_base = db.KnowledgeBaseFinal

# word collection 
word_collection = client["WordCollection"]
positive_words = word_collection["GoodWords"].find({},{'word':1,'_id':0})
negative_words = word_collection["BadWords"].find({},{'word':1,'_id':0})
neutral_words = word_collection["NeutralWords"].find({},{'word':1,'_id':0})

# takes a collection and lookup field. Returns a list of fields from all documents of that collection.   
def get_words(mongo_cursor,lookup_field):
    words = []
    for item in mongo_cursor:
        words.append(item[lookup_field])
    return words

# get all positive negative and neutral words. 
p_words = get_words(positive_words,'word')
n_words = get_words(negative_words,'word')
nu_words = get_words(neutral_words,'word')
    
def show_plot(item1, item2, item3, title):
    barlist = plt.bar(['Positive', 'Negative','Neutral'],[item1,item2,item3])
    barlist[0].set_color('g')
    barlist[1].set_color('r')
    barlist[2].set_color('b')
    plt.title(title)
    plt.show()
    
   
def get_sentiment(selected_entity):
    # initialize pandas dataframe
#    df= pd.DataFrame(columns=["NamedEntity","Descriptive","Sentiment"])   

    good_counter = 0
    bad_counter = 0
    neutral_counter = 0
    try:
        documents = knowledge_base.find({'namedEntity':selected_entity})
    except:
        print("No document with entity: "+ selected_entity)
#    print("--------------------------------------------------------------------------------------------------")
    for document in documents:
        word = document['descriptive']
        if word in p_words:
            good_counter +=1
#            df= df.append({'NamedEntity':selected_entity,'Descriptive':word,'Sentiment':'Positive'},ignore_index=True)
#            print("Positive counter increased "+ word+ " "+ str(good_counter))
        elif word in n_words:
            bad_counter += 1
#            df=df.append({'NamedEntity':selected_entity,'Descriptive':word,'Sentiment':'Negative'},ignore_index=True)
#            print("Negative counter increased " +  word +" "+str(bad_counter))
        elif word in nu_words:
            neutral_counter +=1
#            df=df.append({'NamedEntity':selected_entity,'Descriptive':word,'Sentiment':'Neutral'},ignore_index=True)
#            print("Neutral counter increased "+ word +" "+ str(neutral_counter))
        else:
#            print("Word not found "+ str(word))
            pass
    show_plot(good_counter,bad_counter,neutral_counter, 'Sentiment Analysis of '+selected_entity)
    #append the generated dataframe to our dataset
#    return df
    
#dataset= pd.DataFrame(columns=["NamedEntity","Descriptive","Sentiment"])
df = get_sentiment("Obama")
#dataset = dataset.append(df,ignore_index=True)
#print(dataset)
df = get_sentiment("Trump")
#dataset = dataset.append(df,ignore_index=True)
#print(dataset)
df = get_sentiment("Sanders")
#dataset = dataset.append(df,ignore_index=True)
#print(dataset)
#dataset.to_csv('sentiment_dataset.csv',index=False)