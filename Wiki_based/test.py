import wikipedia
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

class Localizer:

    def __init__(self):
        self.locations = []
        self.texts = []

    def add_SingleLocation(self, location):
        self.locations.append(location)

    def add_listLocation(self, locationList):
        if len(self.locations) == 0:
            self.locations = locationList
        else:
            self.locations = self.locations + locationList

    def get_WikiText(self):
        for l in self.locations:
            p = wikipedia.page(str(l))
            self.texts.append(p.content)

    def printText(self):
        for t in self.texts:
            print(t)

    def get_TFIDF(self):
        transformer = TfidfTransformer(smooth_idf=False)

    def vectorizer(self):
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(self.texts)

        vec = vectorizer.named_steps['vec']
        features = vec.get_feature_names()

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

        print(X)



#TODO: Fetch information from wikipedia - DONE
#TODO: Parse wikipedia page - DONE
#TODO: Get 10;100;1000 top tf-idf words - TBD
#TODO: Give score based on number of words in both sets - TBD
#TODO: choose top 1;5;10 scores and give corresponding states - TBD

test = ["New York State", "New Jersey State"]
#test = ["New York State"]

L = Localizer()
L.add_listLocation(test)
L.get_WikiText()
L.printText()
L.vectorizer()
