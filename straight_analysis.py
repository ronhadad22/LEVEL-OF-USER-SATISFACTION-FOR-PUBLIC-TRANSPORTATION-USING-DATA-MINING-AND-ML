
import os
import convert_to_vec
import glob
not_analysed_files_path = r"D:\semester\final project\BASE CODE\project files\not analysed"
i = 0
for file in glob.glob("*.xlsx"):
    i += 1
    print("CONVI: analysing file", i, file)
    my_tweets_path = os.path.join(not_analysed_files_path, file)  # the file path to be analyzed
    convert_to_vec.main1(my_tweets_path)

'''
q = queue.Queue()
empty = q.empty()
FILES = ["2020_03_17 13", "2020_03_17 15", "2020_03_17 17", "2020_03_17 18", "2020_03_17 19", "2020_03_18 1",
         "2020_03_18 2", "2020_03_18 3", "2020_03_18 4", "2020_03_18 5", "2020_03_18 6", "2020_03_18 7"]

while not empty:  # while THERE IS READY FILES in queue (queue fills up by Streamer)
    print('\nCONVERT_TO_VEC: POP NEW RAEDY_FILE FROM QUEUE')
    pop = q.get()  # pop new file_name to analyze from Queue
    my_tweets_path = os.path.join(MAIN.project_temp_files_path, pop)  # the file path to be analyzed
    convert_to_vec.main1(my_tweets_path)
    empty = q.empty()  # check if queue empty

'''