# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 20:08:41 2019

@author: nsush
"""

import pymongo
from pymongo import MongoClient
import nltk
import re

client = MongoClient('mongodb+srv://sushant_021:pass123@cluster0-rosmg.mongodb.net/test?retryWrites=true&w=majority')
db = client.FinalAssignmentData

# set your knowledge base database from mongodb
knowledge_base = db["KnowledgeBaseFinal"]

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
        
 # get all the collections       
collections = db.list_collection_names()

# go through each collection
for collection_name in collections:
    descriptives=[]
    print("--------------------------------------------------------")
    # see which collection you're working on. 
    print ("Working: "+str(collection_name))
    collection = db[collection_name]
    # go through all the documents of a collection go get the descriptives
    for index,x in enumerate(collection.find()):
        print("Document: "+str(index))
        descriptives.extend(content_processor(x["content"]))
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
        