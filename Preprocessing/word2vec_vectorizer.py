
import gensim

class Word2VecProvider(object):
    word2vec = None
    dimensions = 0

    def load(self, path_to_word2vec):
        self.word2vec = gensim.models.Word2Vec.load_word2vec_format(path_to_word2vec, binary=False)
        self.word2vec.init_sims(replace=True)
        self.dimensions = self.word2vec.vector_size

    def get_vector(self, word):
        if word not in self.word2vec.vocab:
            return None

        return self.word2vec.syn0norm[self.word2vec.vocab[word].index]

    def get_similarity(self, word1, word2):
        if word1 not in self.word2vec.vocab or word2 not in self.word2vec.vocab:
            return None

        return self.word2vec.similarity(word1, word2)


word2vec = Word2VecProvider()

# REPLACE PATH TO THE FILE
word2vec.load("../word2vec_Model")

class TokenizedTwitterData(TwitterData_ExtraFeatures):
    def __init__(self, previous):
        self.processed_data = TwitterData_ExtraFeatures

    tokens = self.processed_data
    current_word2vec = []
    for _, word in enumerate(tokens):
        vec = word2vec_provider.get_vector(word.lower())
        if vec is not None:
            current_word2vec.append(vec)

    tokens = set(self.processed_data.loc[idx, "text"])
    for _, word in enumerate(self.wordlist):
        current_row.append(1 if word in tokens else 0)

    rows.append(current_row)

    averaged_word2vec = list(np.array(current_word2vec).mean(axis=0))
    current_row += averaged_word2vec
