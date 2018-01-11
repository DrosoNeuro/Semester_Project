import wikipedia
import pandas as pd
import numpy as np
import pickle
import string
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer


def top_tfidf_feats(row, features, top_n=25):
    ''' Get top n tfidf values in row and return them with their corresponding feature names.'''
    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    df = pd.DataFrame(top_feats)
    df.columns = ['feature', 'tfidf']
    return df

def top_feats_in_doc(Xtr, features, row_id, top_n=25):
    ''' Top tfidf features in specific document (matrix row) '''
    row = np.squeeze(Xtr[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)

sample_localizations = ['Alabama',
            'Alaska state',
            'Arizona state',
            'Arkansas state',
            'California state',
            'Colorado state',
            'Connecticut state',
            'Delaware state',
            'Florida state',
            'Georgia state',
            'Hawaii state',
            'Idaho state',
            'Illinois state',
            'Indiana state',
            'Iowa state',
            'Kansas state',
            'Kentucky state',
            'Louisiana state',
            'Maine state',
            'Maryland state',
            'Massachusetts state',
            'Michigan state',
            'Minnesota state',
            'Mississippi state',
            'Missouri state',
            'Montana state',
            'Nebraska state',
            'Nevada state',
            'New Hampshire state',
            'New Jersey state',
            'New Mexico state',
            'New York state',
            'North Carolina state',
            'North Dakota state',
            'Ohio state',
            'Oklahoma state',
            'Oregon state',
            'Pennsylvania state',
            'Rhode Island state',
            'South Carolina state',
            'South Dakota state',
            'Tennessee state',
            'Texas state',
            'Utah state',
            'Vermont state',
            'Virginia state',
            'Washington state',
            'West Virginia state',
            'Wisconsin state',
            'Wyoming state',
            'Ontario',
            'Quebec',
            'Nova Scotia',
            'New Brunswick',
            'Manitoba',
            'British Columbia',
            'Prince Edward state',
            'Saskatchewan state',
            'Alberta state',
            'Newfoundland and Labrador state',
            'Washington, D.C. state',
            'Chihuahua state',
            'Baja California state',
            'Freeport bahamas',
            'Nuevo Leon',
              ]

class Localizer:

    def __init__(self):
        self.locations = []
        self.texts = []
        self.X = []
        self.features = []


    def add_SingleLocation(self, location):
        self.locations.append(location)

    def add_listLocation(self, locationList=sample_localizations):
        if len(self.locations) == 0:
            self.locations = locationList
        else:
            self.locations = self.locations + locationList

    def get_WikiText(self):
        translator = str.maketrans('','', string.punctuation)
        for l in self.locations:
            try:
                p = wikipedia.page(str(l))
                s = p.content
                self.texts.append(s.translate(translator))
            except:
                print("Be more specific with " + l)


    def printText(self):
        for t in self.texts:
            print(t)

    def vectorizer(self, language="english"):
        vectorizer = CountVectorizer(stop_words = language)
        self.X = vectorizer.fit_transform(self.texts)
        self.features = vectorizer.get_feature_names()
        return self.X, self.features

    def make_map(self, top):
        self.df = pd.DataFrame(columns=self.locations)
        for n, state in enumerate(self.locations):
            self.df[state] = top_feats_in_doc(self.X, self.features, n, top)['feature']

    def search_for(self, sentence, top=10):
        translator = str.maketrans('','', string.punctuation)
        sentence = sentence.translate(translator)
        results = []
        for state in self.locations:
            results.append((state,sum(self.df[state].str.match('|'.join(sentence.lower().split())))))
        return sorted(results,key=lambda x: x[1], reverse=True)[:top]

    def score(self, sentence, correct_value, top=10):
        res_list = [x[0] for x in self.search_for(sentence, top)]
        return correct_value in res_list




if __name__ == "__main__":
    L = Localizer()
    L.add_listLocation(sample_localizations)
    L.get_WikiText()
    L.vectorizer()
    L.make_map(25)
    print(L.search_for("Alabama, my home, my state"))
    print(L.score('Alabama my home', 'Alabama'))
