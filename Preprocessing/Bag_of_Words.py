from sklearn.feature_extraction.text import CountVectorizer
import pickle
import pandas as pd
import numpy as np
from nltk import TweetTokenizer
import csv
import dask.dataframe as dd
import multiprocessing as mp
import regex as re


tw = pd.read_pickle('Data_W2V/PickledTweets_small.pkl')
# print(tw.head())

#tw['tokenised'].to_csv(path='Data_W2V/tw_large_sentences_Axel.txt', sep=',', index=False, header=False)


#from sent2vec
tknzr1 = TweetTokenizer()
def tokenize(sentence, tknzr=tknzr1,to_lower=True):
    """Arguments:
        - tknzr: a tokenizer implementing the NLTK tokenizer interface
        - sentence: a string to be tokenized
        - to_lower: lowercasing or not
    """
    sentence = sentence.strip()
    sentence = ' '.join([format_token(x) for x in tknzr.tokenize(sentence)])
    if to_lower:
        sentence = sentence.lower()
    sentence = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))','<url>',sentence) #replace urls by <url>
    sentence = re.sub('(\@[^\s]+)','<user>',sentence) #replace @user268 by <user>
    filter(lambda word: ' ' not in word, sentence)
    return sentence

def format_token(token):
    """"""
    if token == '-LRB-':
        token = '('
    elif token == '-RRB-':
        token = ')'
    elif token == '-RSB-':
        token = ']'
    elif token == '-LSB-':
        token = '['
    elif token == '-LCB-':
        token = '{'
    elif token == '-RCB-':
        token = '}'
    return token

dtw_tokens= dd.from_pandas(tw["text"].astype(str).str.replace('\D+', ''), npartitions=mp.cpu_count()-1)
dtw_tokens = dtw_tokens.map(tokenize, meta=dtw_tokens)
tw["tokenised"] = dtw_tokens.compute()

tw.to_pickle("PickledTweets_small_tokenised.pkl")

vectorizer = CountVectorizer()


# test_file = open('Data_W2V/tw_large_sentences_Axel.txt', 'r')
# reader = csv.reader(test_file)
# allRows = [row for row in reader]
# array = vectorizer.fit_transform(allRows).toarray()
array = vectorizer.fit_transform(tw['tokenised']).toarray()

df = pd.DataFrame(array)

df.to_pickle('bow.pkl')
