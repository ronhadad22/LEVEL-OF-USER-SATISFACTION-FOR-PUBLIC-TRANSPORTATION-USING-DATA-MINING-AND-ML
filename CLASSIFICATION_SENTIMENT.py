# Long Short-term Memory (LSTM) for Advanced Text Classification



# Standard Data Management:
import numpy as np
import pandas as pd
# Keras Layers:
from keras.layers import Dense,Input,LSTM,Bidirectional,Activation,Conv1D,GRU
from keras.layers import Dropout,Embedding,GlobalMaxPooling1D, MaxPooling1D, Add, Flatten
from keras.layers import GlobalAveragePooling1D, GlobalMaxPooling1D, concatenate, SpatialDropout1D
# Keras Callback Functions:
from keras.callbacks import Callback
from keras.callbacks import EarlyStopping,ModelCheckpoint
# Various Keras Libraries:
from keras.preprocessing import text, sequence
from keras import initializers, regularizers, constraints, optimizers, layers, callbacks
from keras.models import Model
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
# Sklearn Metrics:
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
import os
from sklearn.metrics import confusion_matrix, f1_score
from textblob import TextBlob
import re
import nltk
from nltk.corpus import stopwords, wordnet

STOPWORDS = nltk.corpus.stopwords.words('english')

# ******** USER INPUTS **********

EMBEDDING_FILE = r"C:\Users\ronha\Downloads\israel_w\‏‏dup1 works with files2\glove.twitter.27B.200d.txt"  # Glove embedding file
Train_path = r'C:\Users\ronha\Downloads\israel_w\‏‏dup1 works with files2\Good_Train_israel.csv'
folder_to_predict = r'C:\Users\ronha\Downloads\israel_w\‏‏dup1 works with files2\temp_geo_final'  # folders of the files to predict
Output_path = r'C:\Users\ronha\Downloads\israel_w\‏‏dup1 works with files2\temp_geo_final\Output.csv'

# CHOOSE WHAT TO DO WITH THW MODEL
test = 1  # 1 - evaluate the model after, show f1 & accuracy results. 0 - don't evaluate
predict = 0  # 1 - make prediction for the given files. 0 - don't make prediction


# *******************************

def get_wordnet_pos(word):
    """
    Map POS tag to first character lemmatize() accepts
    """
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def sentiment_analysis(tweet):  # this function determine the sentiment of tweet based on the polarity of sentence
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0.2:
        return 'Positive'
    elif analysis.sentiment.polarity >= 0:
        return 'Neutral'
    else:
        return 'Negative'


def clean_tweet(tweet):
    """
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    """
    text = re.sub(r'@[A-Za-z0-9]+', '', tweet)  # removed @ mentioned
    text = re.sub(r'#', '', text)  # removed # symbol
    text = re.sub(r'RT[\s]+', '', text)  # removing RT
    text = re.sub(r'https?:\/\/\s+', '', text).split()  # remove the hyper link and split words to list

    # Remove short words (length < 3)
    text = [w for w in text if len(w) > 2]

    lemmatizer = nltk.WordNetLemmatizer()
    text = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in text]

    # Filter out stop words in English
    additional_stop_words = ["sfbart", "bart", "sf", "sfmuni", "muni", "san", "francisco", "business", "sfmta", "th",
                             "amp", "train", "bus", "subway"]
    stops = set(STOPWORDS).union(additional_stop_words)
    # stops = set(stopwords.words('english'))
    text = [w for w in text if w not in stops]

    text = ' '.join(text)
    return text


def main():

    TRAIN = pd.read_csv(Train_path)  # load Train file to Dataframe

    #  ------ load files to predict to Dataframe ( could be .csv or .xlsx) ------
    TEST = pd.DataFrame()
    print("\n***\nloading files to predict... \n***\n")
    # load all files to pandas array before prediction
    for subdir, dirs, files in os.walk(folder_to_predict):
        for file in files:
            filepath = subdir + os.sep + file
            # -------- load file to pandas array ---------
            if filepath.endswith(".csv"):
                pd1 = pd.read_csv(filepath)
            elif filepath.endswith(".xlsx"):
                pd1 = pd.read_excel(filepath)
            TEST = pd.concat([TEST, pd1], ignore_index=True, sort=False)
    print("files loaded")
    TEST = TEST[TEST['text'].notnull()]  # clean null from data
    X_test = TEST['text'].str.lower()  # lowercase all text
    Output = TEST  # save the Dataframe for output usage

    X_train = TRAIN[TRAIN['text'].notnull()]
    y_train = X_train[["target"]].values  # save classes
    X_train = X_train['text'].str.lower()
    X_train1 = X_train

    print("initiate LSTM model")
    max_features = 100000  # number of max words to be used from embedding vocabulary
    max_len = 150  # max length for padding
    embed_size = 200  # embedding vector dimentionality
    batch_size = 128  # number of samples that will be passed through to the network at one time
    epochs = 5  # number of time to give data to the neural network

    tokens =text.Tokenizer(num_words=5000, lower=True)  # initiate tokenizer
    tokens.fit_on_texts(list(X_train)+list(X_test))  # Updates internal vocabulary based on a list of texts

    X_train = tokens.texts_to_sequences(X_train)  # Transforms each text in texts to a sequence of integers
    X_test = tokens.texts_to_sequences(X_test)  # Transforms each text in texts to a sequence of integers
    x_train = sequence.pad_sequences(X_train, maxlen=max_len)  # Pads sequences to the same length
    x_test = sequence.pad_sequences(X_test, maxlen=max_len)  # Pads sequences to the same length

    max_features = len(tokens.word_index) + 1  # number of max words to be used from embedding vocabulary
    embedding_matrix = np.zeros((max_features, embed_size))  # create matrix to maintain the vocabulary that we need

    embeddings_index = {}
    f = open(EMBEDDING_FILE, encoding="utf8")
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()

    for word, i in tokens.word_index.items():  # take only the words vectors needed for us. based on TRAIN and TEST sentences
        if i >= max_features:
            continue
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

    # SET LSTM MODEL
    sequence_input = Input(shape=(max_len, ))  # primary input layer with a size of 150
    x = Embedding(max_features, embed_size, weights=[embedding_matrix], trainable=False)(sequence_input)  # embedding of shape 150 x 200
    x = SpatialDropout1D(0.2)(x)  # This drop dimensions from the embedding matrix for optimization
    x = Bidirectional(GRU(128, return_sequences=True, dropout=0.1, recurrent_dropout=0.1))(x)  # bidirectional layer allowing the model to both forward and back propagate
    x = Conv1D(64, kernel_size=3, padding="valid", kernel_initializer="glorot_uniform")(x)  # implement a convolution layer which creates a convolution kernel that is convolved with the input layer
    avg_pool = GlobalAveragePooling1D()(x)
    max_pool = GlobalMaxPooling1D()(x)
    x = concatenate([avg_pool, max_pool])
    preds = Dense(1, activation="sigmoid")(x)

    if (test):  # evaluation of the model, testing the model with Stratified K-fold
        print("evaluation stage")
        from sklearn.model_selection import StratifiedKFold

        splits = 5  # folds to splits
        skf = StratifiedKFold(n_splits=splits, shuffle=True)
        skf.get_n_splits(x_train, y_train)  # split data to N fold as the number of iteration for the evaluation process
        acc = []  # list of accuracy scores for later averaging
        f1 = []  # list of f1 scores for later averaging
        for train_index, test_index in skf.split(x_train, y_train):  # iterate over different indexes according to choosen folds
            model = Model(sequence_input, preds)  # build new model for every iteration of evaluation stage
            model.compile(loss='binary_crossentropy', optimizer=Adam(lr=1e-3), metrics=['accuracy'])
            # lists to hold the current train folds
            x_Train = []
            y_Train = []
            for index in train_index:  # take train instances using train_index
                x_Train.append(x_train[index])
                y_Train.append(y_train[index])
            # convert to np array
            x_Train = np.array(x_Train)
            y_Train = np.array(y_Train)

            # lists to hold the current test folds
            x_Test = []
            y_Test = []
            for index in test_index:  # take test instances using test_index
                x_Test.append(x_train[index])
                y_Test.append(y_train[index])
            # convert to np array
            x_Test = np.array(x_Test)
            y_Test = np.array(y_Test)

            print("training")
            history = model.fit(x_Train, y_Train, batch_size=batch_size, epochs=epochs, validation_split=0.2, verbose=1)  # training the model
            print('predict one fold of the train')
            y_pred = model.predict(x_Test, batch_size=1024, verbose=1)  # make prediction, return probabilities
            # since the prediction is probabilty, the threshold is being used to determine whether the prediction is 1 or 0
            threshold = 0.5
            y_pred = [1 if x > threshold else 0 for x in y_pred]
            y_pred = np.array(y_pred)

            score = f1_score(y_Test, y_pred, average='micro')  # calc f1 score
            print("f1 micro: ", score)
            print("f1 macro: ", f1_score(y_Test, y_pred, average='macro'))
            f1.append(score)

            confusion_matrix_form = np.array(
                [["true negatives", "false positives"], ["false negatives", "true positives"]],
                np.str)
            print("------- confusion matrix -------")
            cm = confusion_matrix(y_Test, y_pred)
            print(confusion_matrix_form[0], " = ", cm[0])  # ["true negatives", "false positives"]
            print(confusion_matrix_form[1], " = ", cm[1])  # ["false negatives", "true positives"]

            sentences1 = X_train1[test_index]
            sentences = sentences1[y_pred == 1]  # this is the sentences that was classified as related, for debugging
            pass
        print("f1 scores: ", f1)
        print('average f1 score: ', sum(f1) / len(f1))  # average of f1

    if(predict):  # train model and then prediction based on the given train and test files
        model = Model(sequence_input, preds)  # build model for prediction
        model.compile(loss='binary_crossentropy', optimizer=Adam(lr=1e-3), metrics=['accuracy'])

        print("prediction stage")
        X_train, X_validation, y_train, y_validation = train_test_split(x_train, y_train, train_size=0.8, random_state=233)  # split data for the model to train
        print("training ")
        history = model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(X_validation, y_validation), verbose=1)
        print("predicting")
        y_pred = model.predict(x_test, batch_size=1024, verbose=1)
        # since the prediction is probabilty, the threshold is being used to determine whether the prediction is 1 or 0,
        threshold = 0.5
        y_pred = [1 if x > threshold else 0 for x in y_pred]
        y_pred = np.array(y_pred)
        Output['prediction'] = y_pred

        # clean tweets and sentiment analysis
        Output['clean tweets'] = Output['text'].apply(clean_tweet)
        Output['Sentiment'] = Output['clean tweets'].apply(sentiment_analysis)  # apply sentiment analysis

        # export final result file to output path
        Output.to_csv(Output_path)  # save the final result file
        pass



if __name__ == '__main__':
    main()



