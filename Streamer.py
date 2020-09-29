import os

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import main
import sys
import DB_DAL
import analays_tweets
import twitter_credentials
import json
import time
import datetime
from openpyxl import load_workbook

import xlsxwriter


# LIMIT = 100

#determin in which frequence we keep data in mongoDB
NUMBER_OF_TWEETS_PER_UPLOAD = 5

#coordinate of places
GEOBOX_SAN_FRANCISCO = [-122.604, 37.564, -122.253, 37.866]
GEOBOX_Seattle = [-122.3609, 47.5909, -122.3141, 47.6188]
GEOBOX_GERMANY = [5.0770049095, 47.2982950435, 15.0403900146, 54.9039819757]
GEOBOX_NY = [-80, 40.3, -71.7, 45.3]

#count the num of tweets that we collect until is reach to NUMBER_OF_TWEETS_PER_UPLOAD for mongoDB
COUNTER = 0

#if file per hour exist
Flag_file_exist = 0
# close = 0
# tweets = []

db_temp = [None] * NUMBER_OF_TWEETS_PER_UPLOAD


class TwitterAuthenticator():
    # TWITTER AUTHENTICATOR
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth



class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self):
        # This handles Twitter authentication and the connection to Twitter Streaming API
        # לנסות לעשות trace על listener
        listener = TwitterListener()
        auth = self.twitter_autenticator.authenticate_twitter_app()
        while True:
            try:

                stream = Stream(auth, listener)
                #bus shuttles, cable cars
                list_of_words = ['transport','transportation','train ','bus ','subway ']
                stream.filter(track=list_of_words, languages=["en"], locations=GEOBOX_SAN_FRANCISCO)
                # stream.filter( languages=["en"], locations=GEOBOX_SAN_FRANCISCO)
            except:
                print("some error occurred")
                continue



    """
    def fun1( stream ):
        global close
        while True:
            if close == 1:
                stream.disconnect()
                break
    """
        #-------------------------------------




class TwitterListener(StreamListener):
    # counte till NUMBER_OF_TWEETS_PER_UPLOAD and than we upload to the db
    def _init_(self):

        self.api

    #when recieve data from twitter
    def on_data(self, data):
        global COUNTER
        global Flag_file_exist

        try:
            #take the filename by hour and date
            fetched_tweets_filename = main.get_new_name()

            # print(main.TWEETS_COUNT, " ", fetched_tweets_filename)

            # ------------------------------------------------
            #check if we need to start append or to open a new json file
            if main.START_AGAIN == 1:
                main.START_AGAIN = 0
                open(fetched_tweets_filename, "w").close()
            # check if the json file exist
            if os.path.exists(fetched_tweets_filename):
                Flag_file_exist = 1
            else:
                Flag_file_exist = 0

            # append to the json file data return from tweeter
            with open(fetched_tweets_filename, 'a') as fp:
                #data return from tweeter
                relevant_json_date = main.keep_relevant_data(data)
                decoded = json.loads(data)
                # upload tweets to DB.
                db_temp[COUNTER] = relevant_json_date
                if COUNTER == NUMBER_OF_TWEETS_PER_UPLOAD - 1:
                    DB_DAL.DB_Collection.addmany(db_temp, 1)
                    COUNTER = 0
                else:
                    COUNTER = COUNTER + 1
                # upload tweets to DB to second draft.
                if analays_tweets.filter_by_truck(relevant_json_date, 2, 0) == 1:
                    #filter retweets & trump tweets
                    if not decoded["text"].startswith('RT') and decoded["text"].lower().find("trump") < 0:

                        main.increment()
                        #prepare json file to be valid
                        if Flag_file_exist == 1 and os.stat(fetched_tweets_filename).st_size > 0:
                            if not check_last_char(fetched_tweets_filename, ','):  # return False if the last char is not ',' -----תיקנתי------------------
                                fp.write(",")
                        else:
                            fp.write("[")
                        #append data to the json file
                        fp.write(json.dumps(relevant_json_date))
                        fp.write("\n")

                # DB_DAL.DB_Collection.addOne(relevant_json_date, 1)

        except BaseException as e:
            print('\033[93m' + "Error on data: %s" % str(e) + '\033[0m')
            return True
        # --------------------------------israel addition--automation--------------------------------------------
        # ts = time.time()
        # st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')

        now = datetime.datetime.now()

        #check evry hour if need to close json file
        if (now.minute > 50 and main.H == 100) or ((now.hour - main.H) >= 1) or (now.hour == 00 and main.H == 23):
            main.TWEETS_COUNT = 0
            #close json
            with open(fetched_tweets_filename, 'a') as fp:
                if os.stat(fetched_tweets_filename).st_size != 0:
                    fp.write("]")


            main.H=datetime.datetime.now().hour
            main.ST = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d')
            main.START_AGAIN = 1

            #return False  # If on_data returns False, the connection will be shut down
        # --------------------------------------------------------------------------------------------


    def on_error(self, status):
        # twitter try to stop the request
        if status == 420 or status == 401:
            # Returning False on_data method in case rate limit occurs.
            time.sleep(60)
            pass
        time.sleep(60)
        print(status)

    def on_disconnect(self, notice):
        print("disconnect!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def on_connect(self):
        print("connect!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")



#check the last char value in file
def check_last_char(file, char):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
        last_char = last_line[-1]
    return last_char == char
