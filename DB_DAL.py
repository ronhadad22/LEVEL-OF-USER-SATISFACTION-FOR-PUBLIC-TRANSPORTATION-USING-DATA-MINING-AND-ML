import pymongo

from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

import json

class DB_Collection():
    #keep the collection info after the connatction
    #DB = None;
    #$$$ לסדר חיבורים כפולים
    #$$לבדוק חיפוש ושליפה נכונה בdb



    def connection_to_collection (Collection_name):
        try:
            url = "mongodb://carmel_sahar:i2n9b1aR@ds213615.mlab.com:13615/twitter"
            connection = MongoClient(url, port=27017)
            DB = connection['twitter']
            if Collection_name == 1:
                Collection = DB['first_filter_DB ']
            #Collection = DB['second_filter_DB_2']
            if Collection_name == 2:
                Collection = DB['second_filter_DB']
            if Collection_name == 3:
                Collection = DB['second_filter_DB_2']
            print('\033[94m'+"connected to db"+'\033[0m')
        except:
            print('\033[93m'+"connection problem"+'\033[0m')
        return Collection




    def addOne(data_for_upload, Collection_name):
        data = data_for_upload
        Collection = DB_Collection.connection_to_collection(Collection_name)
        try:
            """if data['_id']==None:
                oNum = ObjectId
                newData = {'_id': oNum, 'tweet': data}"""
            data['_id'] = ObjectId()
            Collection.insert_one(data)
            print('\033[94m'+"add success"+'\033[0m')
        except:
            print('\033[93m'+"insert problem"+'\033[0m')

    def addmany(data_for_upload, Collection_name):
        data = data_for_upload
        index = 0
        #$$$$$ לשאול
        Collection = DB_Collection.connection_to_collection(Collection_name)
        try:
            for tweet in data:
                oNum = data[index]['id']
                data[index] = {'_id': oNum, 'tweet': data[index]}
                index = index +1
            Collection.insert_many(data)
            print('\033[94m'+"add success"+'\033[0m')
        except:
            print('\033[93m'+"insert problem"+'\033[0m')

    def findAll(Collection_name):
        Collection = DB_Collection.connection_to_collection(Collection_name)
        try:
            cursor = Collection.find({})
            return cursor
        except:
            print('\033[93m'+"find problem"+'\033[0m')
