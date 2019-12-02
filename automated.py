# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 01:20:25 2019

@author: nsush
"""
import urllib3
import certifi
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pymongo
import nltk
import re
import matplotlib.pyplot as plt
import pandas as pd

# mongo client
client = MongoClient('mongodb+srv://sushant_021:pass123@cluster0-rosmg.mongodb.net/test?retryWrites=true&w=majority')
db = client.Automated

#header for http request
user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}


#takes a name and gives nytimes url for that name
def process_name(name):
    names = name.split()
    word = ''
    for name in names:
        word += name
        if names[-1] == name:
            pass
        else:
            word += '-'
    name=word.lower()
    url = 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/topic/person/'+name+'/rss.xml'
    return url

# scrapes data from the given url and stores in the given collection name
def ScrapeAndStore(url,collection_name):
    #check if a same collection already exists. If exists, drop it. 
    if collection_name in db.list_collection_names():
        db[collection_name].drop()
        
    col_name = db[collection_name]
    
    # get request to retrieve the xml file  
    try:
        r = http.request('GET',url,headers= user_agent)
        if r.status == 404:
            print("Nobody found with that name.Are you sure that's the name? For example Warrent Buffet is wrong. It's Warren E Buffet. ")
            return 0
    except:
        print("Somethin wroong with http.")
    # decoding the source code in utf-8 format
    sourceCode = r.data.decode('utf-8')
    
    # all the links to articles retrieved from the xml file.
    links = re.findall(r'<link>(.*?)</link>',sourceCode)
    if len(links) == 0:
        print("Are you sure that's the name? For example Warrent Buffet is wrong. It's Warren E Buffet.")
        exit()
    
    # the top link is a link to the main site. We don't need that. So we leave first 
    # and take the rest of the links
    links = links[1:]
    
    # loop through each link to visit the article page and retrieve the article
    for link in links:
        print("----------------------------------------------------------------")
        print("Visiting link:"+link)
        r = http.request('GET',link,headers= user_agent)
        sourceCode = r.data.decode('utf-8')
        # parse the source code with beautiful soup
        soup = BeautifulSoup(sourceCode, "html.parser")
        
        #content = soup.find_all("p",class_="g-body",id="")
        # the article body is inside the <p class="css-exrw3m evys1bk0></p>.
        # So, get all the contents. 
        # the contents returned by fidn_all is a list of elements / paragraphs found. 
        contents = soup.find_all("p",class_="css-exrw3m evys1bk0")
        # initialize a empty paragraph 
        para = ''
        # concatenate all the paragraphs
        for content in contents:
            para += str(content.next)
#        print(para)
        # create an article object to store in mongo database
        article = {
                'link':link,
                'content':para
                }
        # insert one article 
        col_name.insert_one(article)
        print("One row inserted in: "+str(col_name))
        
        
#-----------------------------------------------------------------------------


# processes each line to print descriptives from that line
def line_processor(line):
    try:
        tokenized = nltk.word_tokenize(line)
        tagged = nltk.pos_tag(tokenized)
        named_entity = nltk.ne_chunk(tagged,binary = True)
        entities = re.findall(r'NE\s(.*?)/',str(named_entity))
        descriptives = re.findall(r'\(\'(\w*)\',\s\'JJ\w?\'', str(tagged))  
        # print(entities)
        # just need the descriptives
#        if len(descriptives) != 0:
#            print(descriptives)       
        return descriptives
         
    except:
        print("Failed in line processor")

# takes content from each document and returns a list of descriptives from that document
def content_processor(data):
    try:
        a_list = []
        lines = data.split(".")
        for eachline in lines:
            a_list.extend(line_processor(eachline))
        return a_list
                     
    except:
        print("Failed in content processor")


# create knowledge base from given collection  
def create_knowledge_base(collection_name):
    #init an empty descriptive list for later to store
    descriptives=[]
    #get the collection
    collection = db[collection_name]
    # go through all the documents of a collection go get the descriptives
    for index,x in enumerate(collection.find()):
        print("Processing Document: "+str(index))
        descriptives.extend(content_processor(x["content"]))
    
    print('Building up knowledge base. Takes some time...')
      
    # store each descriptive in knowledge base with corresponding collection name
    for item in descriptives:
        row = {
                'namedEntity':str(collection_name),
                'descriptive':item
              }
        # just checking for words like's' or 're'
        if len(item) < 3:
            pass
        else:
            knowledge_base.insert_one(row)
    print(str(len(descriptives))+" rows inserted in collection: "+ str(collection_name))
    
#-------------------------------------------------------------------------------------------


# takes a collection and lookup field. Returns a list of fields from all documents of that collection.   
def get_words(mongo_cursor,lookup_field):
    words = []
    for item in mongo_cursor:
        words.append(item[lookup_field])
    return words



# show a bar plot
def show_plot(item1, item2, item3, title):
    barlist = plt.bar(['Positive', 'Negative','Neutral'],[item1,item2,item3])
    barlist[0].set_color('g')
    barlist[1].set_color('r')
    barlist[2].set_color('b')
    plt.title(title)
    plt.show()
    

# gets sentiment of the given name, the name here is just a string for plot title and namedEntity for dataset
def get_sentiment(name):
    print("Processing sentiment analysis...")
#   initialize pandas dataframe
    df= pd.DataFrame(columns=["NamedEntity","Descriptive","Sentiment"])   
    
    # set your knowledge base database 
    knowledge_base = db[collection_name+"-KB"]
    
    good_counter = 0
    bad_counter = 0
    neutral_counter = 0
    try:
        documents = knowledge_base.find({})
    except:
        print("No documents found.")
#    print("--------------------------------------------------------------------------------------------------")
    for document in documents:
        word = document['descriptive']
        if word in p_words:
            good_counter +=1
            df= df.append({'NamedEntity':name,'Descriptive':word,'Sentiment':'Positive'},ignore_index=True)
#            print("Positive counter increased "+ word+ " "+ str(good_counter))
        elif word in n_words:
            bad_counter += 1
            df=df.append({'NamedEntity':name,'Descriptive':word,'Sentiment':'Negative'},ignore_index=True)
#            print("Negative counter increased " +  word +" "+str(bad_counter))
        elif word in nu_words:
            neutral_counter +=1
            df=df.append({'NamedEntity':name,'Descriptive':word,'Sentiment':'Neutral'},ignore_index=True)
#            print("Neutral counter increased "+ word +" "+ str(neutral_counter))
        else:
#            print("Word not found "+ str(word))
            pass
    show_plot(good_counter,bad_counter,neutral_counter, 'Sentiment Analysis of '+name)
    #append the generated dataframe to our dataset
    return df

#donald_trump_url = 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/topic/person/donald-trump/rss.xml'
name = input("Give me a name of popular US politician: ")
url = process_name(name)

collection_name = name.replace(" ","").lower()
# set your knowledge base database 
knowledge_base = db[collection_name+"-KB"]

# word collection monggo db collections
word_collection = client["WordCollection"]
positive_words = word_collection["GoodWords"].find({},{'word':1,'_id':0})
negative_words = word_collection["BadWords"].find({},{'word':1,'_id':0})
neutral_words = word_collection["NeutralWords"].find({},{'word':1,'_id':0})

# get all positive negative and neutral words. 
p_words = get_words(positive_words,'word')
n_words = get_words(negative_words,'word')
nu_words = get_words(neutral_words,'word')


response = ScrapeAndStore(url,collection_name)
if response == 0:
    pass
else:
    create_knowledge_base(collection_name)
    # just passing the original name just for the title of plot and for the dataset
    df = get_sentiment(name)
    df.to_csv(name+'.csv',index=False)





