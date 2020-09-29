import json
import os
import DB_DAL
import re

def filter_by_truck(tweets, mode_from, mode_DB):
    # list_of_words = ['bus ', 'transportation', 'BART', 'Muni', 'Muni metro', 'Sfmta', 'Cable car', 'Clipper card', 'Trolley','Streetcar', 'Tram', 'Fillmore', 'Stanyan'  , 'Geary' , 'Noriega']
    list_of_words = ['transport','#transport','transportation','#transportation','train','#train','bus','#bus','subway','#subway']
    index_of_relevant_tweets = 0
    dict_after_truck = dict()
    if mode_from == 1:
        text = tweets["tweet"]["text"]
    if mode_from == 2:
        text = tweets["text"]
    if mode_DB == 3:
        list_of_words = ['transport','#transport','transportation','#transportation','train','#train','bus','#bus','subway','#subway']
    # if 'bus' in text:
    words_re = re.compile("|".join(list_of_words))
    if words_re.search(text.lower()):
        print("--------------")
        index_of_relevant_tweets = index_of_relevant_tweets + 1
        #print("success", index_of_relevant_tweets)
        dict_after_truck[index_of_relevant_tweets] = tweets
        if mode_from == 1:
            return 1
        if mode_from == 2:
            return 1
            print(dict_after_truck[index_of_relevant_tweets]["text"])
            DB_DAL.DB_Collection.addOne(tweets, 2)

def basic_filter_by_truck(tweet):
    list_of_words = ['transport','#transport','transportation','#transportation','train','#train','bus','#bus','subway','#subway']
    #index_of_relevant_tweets = 0
    #dict_after_truck = dict()
    text = tweet["text"]
    words_re = re.compile("|".join(list_of_words))
    for word in list_of_words:
        if re.search(word, text, re.IGNORECASE):# if the word exists in the text ( incasesensitive )
            #index_of_relevant_tweets = index_of_relevant_tweets + 1
            #print("success", index_of_relevant_tweets)
            return 1
    return 0


def filter_file_by_truck(tweets_arr, mode_DB):
    dict_after_truck = dict()
    index_of_relevant_tweets = 0
    for tweet in tweets_arr:
        if filter.filter_by_truck(tweet, 1) == 1:
            dict_after_truck[index_of_relevant_tweets] = tweet
            print(dict_after_truck[index_of_relevant_tweets]["tweet"]["text"])
    DB_DAL.DB_Collection.addmany(dict_after_truck, mode_DB, 2, mode_DB)