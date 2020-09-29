
import os
import main
import numpy as np
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import main
import time
import datetime

import sentiment_analysis
matplotlib.use('TkAgg')
filename = ''


def plot_roc(clf, X_test, y_test):
    y_pred = clf.predict(X_test)
    fpr, tpr, _ = roc_curve(y_test, y_pred)
    plt.plot(fpr, tpr)
    plt.xlabel('FPR')
    plt.ylabel('TPR')


def print_scores(clf, X_train, y_train, X_test, y_test):
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_train)
    print('F1 score: {:3f}'.format(f1_score(y_train, y_pred)))
    print('AUC score: {:3f}'.format(roc_auc_score(y_train, y_pred)))

def main1():
    train_to_vec_path = os.path.join(main.project_temp_files_path, "train_to_vectors.csv")  # train data file
    my_tweets_to_vec_path = os.path.join(main.project_temp_files_path, "my_tweets_to_vectors.csv")

    print('APPLYING ML: Reading in train to vectors...')
    train_data = pd.read_csv(train_to_vec_path, encoding='ISO-8859-1', low_memory=False)
    train_data.columns
    train_data.memory_usage(deep=True).sum()
    train_data['RT'].value_counts()

    a = train_data.iloc[:, 2:302]

    X_resample = a.values  # takes only the vectors rows
    # print("X_resample", type(X_resample), "\n", X_resample)
    b = train_data.iloc[:, 302]

    y_resample = b.values  # takes only 1 column, the RT
    # print("y_resample", type(y_resample), "\n" ,y_resample)

    X_train, X_test, y_train, y_test = train_test_split(X_resample, y_resample, stratify=y_resample, random_state=0)

    '''
    print("X_train", type(X_train), X_train)


    print("X_test", type(X_test), X_test)


    print("y_train", type(y_train), y_train)


    print("y_test", type(y_test), y_test)
    '''

    rf = RandomForestClassifier(oob_score=True).fit(X_train, y_train)  # model
    y_pred = rf.predict(X_test)
    print_scores(rf, X_train, y_train, X_test, y_test)
    # plot_roc(rf, X_test, y_test)
    print('APPLYING ML: Score: ', rf.score(X_test, y_test))
    oob_error = 1 - rf.oob_score_

    print("APPLYING ML: OOB error is: " + str(oob_error))
    # plt.show()

    print("APPLYING ML: reading my tweets to vectors")
    test_data = pd.read_csv(my_tweets_to_vec_path, encoding='ISO-8859-1', low_memory=False)  # the file from carmel after we convert it to vectors

    X = test_data.iloc[:, 4:304].values

    y_pred = rf.predict_proba(X)
    y_pred = y_pred[:, 1]

    sub = pd.DataFrame(y_pred, columns=['RT'])

    sub['id'] = test_data['id']
    sub['text'] = test_data['text']
    sub['geotag'] = test_data['geotag']
    sub['time'] = test_data['time']
    # sub.loc[sub["RT"] > 0.3, 'my_channel'] = 1

    sub['que'] = np.where((sub["RT"] > 0.3), 1, 0)
    cols = sub.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    sub = sub[cols]
    #  output file
    filename = "sub_v" + str(main.FILE_NUM) + "_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d')\
               + "_" + str(datetime.datetime.now().hour) + ".csv"
    sub.to_csv(filename, index=False)
    print("APPLYING ML: FINISH FILE, " + filename + " has been saved")
    main.START_AGAIN = 1
    sentiment_analysis.main1(filename)


if __name__ == '__main__':
    main1()




"""
print("Plotting feature importance...")
vecs = []
for i in range(1,300):
    print(i)
    vecs.append("v"+str(i))

top_n=100
figsize=(8,36)
title="Feature Importances"
feat_imp = pd.DataFrame({'importance':rf.feature_importances_})    
feat_imp['feature'] = vecs
feat_imp.sort_values(by='importance', ascending=False, inplace=True)
feat_imp = feat_imp.iloc[:top_n]
feat_imp.sort_values(by='importance', inplace=True)
feat_imp = feat_imp.set_index('feature', drop=True)
feat_imp.plot.barh(title=title, figsize=figsize)
plt.xlabel('Feature Importance Score')
plt.show()
"""