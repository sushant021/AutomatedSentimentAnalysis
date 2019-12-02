# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 14:53:50 2019

@author: nsush
"""
import urllib3
import certifi
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pymongo

# mongo client
client = MongoClient('mongodb+srv://sushant_021:pass123@cluster0-rosmg.mongodb.net/test?retryWrites=true&w=majority')
db = client.FinalAssignmentData

#header for http request
user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}

# urls to get xml data for each person.
donald_trump_url = 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/topic/person/donald-trump/rss.xml'
barack_obama_url = 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/topic/person/barack-obama/rss.xml'
bernard_sanders_url = 'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/topic/person/bernard-sanders/rss.xml'

# url dict created to loop through each person. More persons can be added with ease if required.
url_dict = {'Trump':donald_trump_url,'Obama':barack_obama_url,'Sanders':bernard_sanders_url}

# scrapes data from the given url and stores in the given collection name
def ScrapeAndStore(url,col_name):
    #col_name is passed as string. So, just changing it into a collection object. 
    if col_name == 'Trump':
        col_name = db.Trump
    elif col_name == 'Obama':
        col_name= db.Obama
    else:
       col_name = db.Sanders
    
    # get request to retrieve the xml file    
    r = http.request('GET',url,headers= user_agent)
    # decoding the source code in utf-8 format
    sourceCode = r.data.decode('utf-8')
    
    # all the links to articles retrieved from the xml file.
    links = re.findall(r'<link>(.*?)</link>',sourceCode)
    
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
   
# drop pre existing databases 
db.Trump.drop()
db.Sanders.drop()
db.Obama.drop()

# loop through 3 users. 
for name,url in url_dict.items():
    ScrapeAndStore(url,name)


