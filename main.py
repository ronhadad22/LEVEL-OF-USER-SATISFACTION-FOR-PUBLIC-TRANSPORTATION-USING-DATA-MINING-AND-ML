import time
import datetime
import Streamer
import json
from threading import Thread
import queue
import save_csv_file
import CLASSIFICATION_SENTIMENT

TWEETS_COUNT = 0
START_AGAIN = 1
FILE_NUM = 0
Original_file_name = "tweets_filter_San_F_"
TS = time.time()
ST = datetime.datetime.fromtimestamp(TS).strftime('%Y_%m_%d')
H = 100
RON_COUNT_GEO_RE = 0
RON_COUNT_GEO = 0
def increment():
    # adding 1 to the tweets_counter
    global TWEETS_COUNT
    TWEETS_COUNT = TWEETS_COUNT + 1


def keep_relevant_data(data_Original):
    """The function copy the important part of the original data to a new dict
:param data_Original:
:return: a variable of type dict which contains only the relevant information from the tweet
"""
    json_data = json.loads(data_Original)

    # print(json_data)

    new_json_file = {}
    new_json_file["created_at"] = json_data["created_at"]
    new_json_file["id"] = json_data["id"]
    new_json_file["text"] = json_data["text"]

    new_json_file["source"] = json_data["source"]
    new_json_file["user"] = {}
    new_json_file["user"]["id"] = json_data["user"]["id"]
    new_json_file["user"]["name"] = json_data["user"]["name"]
    new_json_file["user"]["screen_name"] = json_data["user"]["screen_name"]
    new_json_file["user"]["location"] = json_data["user"]["location"]

    new_json_file["user"]["followers_count"] = json_data["user"]["followers_count"]
    new_json_file["user"]["friends_count"] = json_data["user"]["friends_count"]
    new_json_file["user"]["statuses_count"] = json_data["user"]["statuses_count"]
    new_json_file["user"]["geo_enabled"] = json_data["user"]["geo_enabled"]
    new_json_file["geo"] = json_data["geo"]
    new_json_file["coordinates"] = json_data["coordinates"]
    # if json_data["extended_entities"] != None:
    #     print("extended_entities")
    #     new_json_file["extended_entities"] = new_json_file["extended_entities"]
    #     print(json_data["extended_entities"])
    if 'entities' in json_data:
    # if json_data["entities"]["media"]["media_url"] != None:
        print("entities")
        print(json_data["entities"])
        if 'media' in json_data["entities"]:
            print("media_ron")
            new_json_file["media_url"] = json_data["entities"]["media"][0]["media_url_https"]
            # print(json_data["entities"]["media"][0])
            # print(new_json_file["entities"]["media"][0]["media_url_https"])
        else:
            new_json_file["media_url"] = "None"
    else:
        new_json_file["media_url"] = "None"
    if str(new_json_file["coordinates"]) != 'None':
        global RON_COUNT_GEO
        RON_COUNT_GEO = RON_COUNT_GEO+1;
        print("ron_geo:")
        print(new_json_file["source"])
        if str(new_json_file[
                   'source']) == r'<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>' or str(
            new_json_file[
                'source']) == r'<a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>' or str(
            new_json_file[
                'source']) == '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>':
            global RON_COUNT_GEO_RE
            RON_COUNT_GEO_RE = RON_COUNT_GEO_RE+1


    new_json_file["place"] = json_data["place"]
    print("RON_COUNT_GEO_RE: "+str(RON_COUNT_GEO_RE))
    print("RON_COUNT_GEO: "+str(RON_COUNT_GEO))

    return new_json_file



def get_new_name():
    """
    getting the correct date ang edd it to the file name
    :return: the correct file name.
    """
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
    #return Original_file_name + st + ".json"
    return "json_output/"+str(st)+str(datetime.datetime.now().hour)+"temp_t.json"


def stream_func():
    print("THREAD 1 START: STREAMER")
    twitter_streamer = Streamer.TwitterStreamer()
    twitter_streamer.stream_tweets()


def file_saving_func():
    print("THREAD 2 START: HOURLY FILE SAVER")
    save_csv_file.save_file_every_hour()


def convert_to_vec_func():
    print("THREAD 3 START: CONVERT_TO_VEC")
    CLASSIFICATION_SENTIMENT.main()


fetched_tweets_filename = get_new_name()


def main():

    streaming_thread = Thread(target=stream_func)  # this thread handle the streaming tweets
    saving_file_thread = Thread(target=file_saving_func)  # this thread save the file of collected tweets every hour
    convert_to_vec_thread = Thread(target=convert_to_vec_func)  # convert to vec will start everytime new file is ready to be analyzed

    streaming_thread.start()
    saving_file_thread.start()
    convert_to_vec_thread.start()

    streaming_thread.join()
    saving_file_thread.join()
    convert_to_vec_thread.join()


if __name__ == '__main__':
    main()
    print("\nMAIN: THREADS FINISH THEIR JOB")