
# import json
import sys
import os
import re
import gensim
import nltk
import main as MAIN
# import numpy as np
import xlsxwriter
from openpyxl import load_workbook
from keras.preprocessing import sequence
import csv
import xlrd
from gensim.models import Word2Vec
import applying_ML_algorithms
from datetime import datetime
import time as time_module
import Streamer
import time
import glob
import queue

convert_to_vec_file_exist = 0  # flag: prevent recreation of convert_to_vec file


STOPWORDS = nltk.corpus.stopwords.words('english')

emoticons_str = r"""
		(?:
			[:=;] # Eyes
			[oO\-]? # Nose (optional)
			[D\)\]\(\]/\\OpP] # Mouth
		)"""

regex_str = [
    emoticons_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs
    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)'  # other words
    # r'(?:\S)'  # anything else
]

number_str = r'(?:(?:\d+,?)+(?:\.?\d+)?)'
tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)
number_re = re.compile(r'^' + number_str + '$', re.VERBOSE | re.IGNORECASE)




header = []


def tokenize(s):
    return tokens_re.findall(s)


def preprocess(s):
    tokens = tokenize(s)
    # tokens = [token.lower() if emoticon_re.search(token) == False and token not in STOPWORDS else  for token in tokens]
    tokens = map(lambda token: token.lower(),
                 filter(lambda token: emoticon_re.search(token) is None
                                      and token not in STOPWORDS
                                      and token.find('http') == -1
                                      and number_re.search(token) is None
                        , tokens))

    return tokens


def load_google_word2vec_model():
    path = os.path.join(MAIN.project_temp_files_path, "GoogleNews-vectors-negative300.bin")
    google_model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)
    return google_model


def how_many(str, char):
    count = 0
    for i in range(0, len(str)-1):
        if str[i] == char:
            count = count + 1
    return count


def convert_train_to_vec(train_path, google_model):
    # convert train file to vectors file and save it
    print("\nCONVERT_TO_VEC: converting train to vec")
    max_review_length = 300
    header = []
    train_to_vec_path = os.path.join(MAIN.project_temp_files_path, "train_to_vectors.csv")
    header.append('id')
    header.append('text')
    for k in range(1, 301):
        # str = 'v{}'.format(i-1)
        # header.append(locals()[str])
        my_str = "v%s" % (k)
        header.append(my_str)
    header.append('RT')

    feature_file = open(train_to_vec_path, 'w', encoding='utf-8')  # output file here
    feature_file.writelines(','.join(map(str, header)) + '\n')

    with open(train_path, 'r', encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        next(reader)
        for line in reader:
            id = line[0]
            text = line[1]  # [id,text]

            data_dict = line
            sentence = preprocess(data_dict[1])  # takes the text
            sentence_vector = []
            for word in sentence:
                try:
                    tmp_vec = google_model.word_vec(word).tolist()  # np.array([1,1,1,1]).tolist()
                    # tmp_vec = model.wv.word_vec(word).tolist()
                except:
                    e = sys.exc_info()[0]
                    print("CONVERT_TO_VEC: our model did not learn the word", word, "  <p>Error: %s</p>" % e)
                    tmp_vec = []

                sentence_vector += tmp_vec

            dummy_list = []
            # dummy_list.append(data_dict[0])
            # dummy_list.append(data_dict[1])
            # dummy_list.append(data_dict[2])
            # dummy_list.append(data_dict[3])
            dummy_list.append(sentence_vector)
            sentence_vector = dummy_list
            # print("1")
            # print(sentence_vector)
            sentence_vector = sequence.pad_sequences(sentence_vector,
                                                     maxlen=max_review_length,
                                                     padding='post', truncating='post',
                                                     dtype='float32')
            sentence_vector = sentence_vector[0]
            text = '"' + re.sub('"', '', text) + '"'
            feature_file.writelines(
                id + ' ,' + text + ' ,' + ','.join(map(str, sentence_vector)) + ' ,' + line[2] + '\n')


def convert_my_tweets_to_vec(inpath, google_model):
    # convert tweet file to vectors file and save it
    print('\nCONVERT_TO_VEC: converting my tweets to vectors')

    max_review_length = 300
    header = []
    my_tweets_to_vec_path = os.path.join(MAIN.project_temp_files_path, "my_tweets_to_vectors.csv")
    header.append('id')
    header.append('text')
    header.append('geotag')
    header.append('time')
    for k in range(1, 301):
        my_str = "v%s" % k
        header.append(my_str)
    feature_file = open(my_tweets_to_vec_path, 'w', encoding='utf-8')  # output file here
    feature_file.writelines(','.join(map(str, header)) + '\n')

    #with open(inpath, 'r', encoding='ISO-8859-1') as f:
    wb = xlrd.open_workbook(inpath)
    sheet = wb.sheet_by_index(0)
    # sheet = wb.active
    maxRow = sheet.nrows
    for line in range(1, maxRow):
        id = '"' + str(sheet.cell_value(line, 0)) + '"'
        text = '"' + re.sub('"', '', str(sheet.cell_value(line, 1))) + '"'
        geotag = '"' + str(sheet.cell_value(line, 2)) + '"'
        time = '"' + str(sheet.cell_value(line, 3)) + '"'

        sentence = preprocess(text)  # takes the text
        sentence_vector = []
        for word in sentence:

            try:
                tmp_vec = google_model.word_vec(word).tolist()  # np.array([1,1,1,1]).tolist()
                # tmp_vec = model.wv.word_vec(word).tolist()
            except:
                e = sys.exc_info()[0]
                print("CONVERT_TO_VEC: our model did not learn the word", word, "  <p>Error: %s</p>" % e)
                tmp_vec = []

            sentence_vector += tmp_vec
        dummy_list = []
        # dummy_list.append(data_dict[0])
        # dummy_list.append(data_dict[1])
        # dummy_list.append(data_dict[2])
        # dummy_list.append(data_dict[3])
        dummy_list.append(sentence_vector)
        sentence_vector = dummy_list
        sentence_vector = sequence.pad_sequences(sentence_vector,
                                                 maxlen=max_review_length,
                                                 padding='post', truncating='post',
                                                 dtype='float32')
        sentence_vector = sentence_vector[0]
        feature_file.writelines(
            id + ' ,' + text + ' ,' + geotag + ' ,' + time + ' ,' + ','.join(map(str, sentence_vector)) + '\n')
    feature_file.close()


def main1(my_tweets_path):  # file path = the MY_TWEETS file to convert
    google_model = load_google_word2vec_model()

    train_path = os.path.join(MAIN.project_temp_files_path, "train_new.csv")

    global convert_to_vec_file_exist
    if not convert_to_vec_file_exist:  # flag: train_to_vec already created before
        convert_train_to_vec(train_path, google_model)
        convert_to_vec_file_exist = 1

    convert_my_tweets_to_vec(my_tweets_path, google_model)

    applying_ML_algorithms.main1()


def fill_and_print_queue(fill=1):  # if fill = 1, the function fill the Queue according to folder 'Queue'

    queue_files_path = os.path.join(MAIN.queue_path, '*.xlsx')
    base = 40  # the width of the Queue to print
    first = 1

    for n in range(0, 2):
        i = 0
        print("|", end="")
        while i < int(2*base) - 2:
            i += 1
            print(" ", end="")
        print("|")

    if base % 2 != 0:
        base1 = int(base)
        base2 = int(base)
    else:
        base1 = int(base) - 1
        base2 = int(base) - 1
    i = 0

    print("|", end="")
    while i < base1 - 3:  # - "QUE
        i += 1
        print("-", end="")
    print("Queue", end="")
    i = 0
    while i < base2 - 2:  # - "UE
        i += 1
        print("-", end="")
    print("|")

    for n in range(0, 2):
        print("|", end="")
        i = 0
        while i < int(2*base) - 2:
            i += 1
            print(" ", end="")
        print("|")

    for file in glob.glob(queue_files_path):
        file_name = os.path.split(file)[1]
        if fill == 1:  # fill the Queue
            MAIN.Queue_pointer.put(file_name)  # add new file to queue, for convert_to_vec
        print('|', end="")
        len_ = int(len(file_name))
        if (len_ % 2) != 0:
            len1 = base - int(len_ / 2)
            len2 = base - (int(len_ / 2) + 1)
        else:
            len1 = len2 = base - int(len_ / 2)
        for i in range(1, len1):
            print(" ", end="")
        print(file_name, end="")
        for i in range(1, len2):
            print(" ", end="")
        if first == 1:
            print('|', end="")
            print("<---- HEAD, FIFO")
            first = 0
        else:
            print('|')
    for i in range(0, 2*base):
        print("-", end="")


def main():
    # check the queue every hour
    global convert_to_vec_file_exist
    convert_to_vec_file_exist = 0
    sleep_time = 3600  # time in sec, until the next Queue check
    fill_and_print_queue(1)  # fill Queue with files from "physical folder- 'Queue'"
    while True:
        empty = MAIN.Queue_pointer.empty()  # check if queue empty
        while not empty:  # while THERE IS READY FILES in queue (queue fills up by Streamer)
            poped_file_path = os.path.join(MAIN.project_temp_files_path, 'Queue')  # the file path to be analyzed
            pop = MAIN.Queue_pointer.get()  # pop new file_name to analyze from Queue
            print('\nCONVERT_TO_VEC: POP QUEUE TO ANALYSE, FILE NAME: ', pop)
            poped_file_path = os.path.join(poped_file_path, pop)  # the file path to be analyzed
            main1(poped_file_path)
            # --------delete file from physical folder----------
            os.remove(poped_file_path)
            # -----------------
            print("CONVERT_TO_VEC: Finish FILE: ", pop)
            fill_and_print_queue(0)  # print without filling Queue
            empty = MAIN.Queue_pointer.empty()  # check if queue empty
        if empty:
            print("\nCONVERT_TO_VEC: TIME IS: " + str(datetime.now().hour) + ":" + str(datetime.now().minute) + " 0 files in Queue")
            print("\n\n\n\n\n\n\n\n\n\n going to sleep for ", sleep_time, "sec")
            time.sleep(sleep_time)


if __name__ == '__main__':
    main()


