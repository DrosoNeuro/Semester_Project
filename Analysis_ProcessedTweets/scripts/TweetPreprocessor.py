#adapted from Arno Schneuwly
from nltk import TweetTokenizer
import re

class TweetPreprocessor:
    def __init__(self):
        self.tknzr = TweetTokenizer()

    def _preprocess_tweet(self, tweet):
        tweet = " ".join(tweet.splitlines()) # remove all newline characters
        tweet = tweet.lower()
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', '<url>', tweet) #replace urls by <url>
        tweet = re.sub('(\@[^\s]+)', '<user>', tweet) #replace @user268 by <user>
        tweet = re.sub('\0', " ", tweet)
        tweet = re.sub('\t', " ", tweet)
        tweet = " ".join(tweet.split())
        return tweet

    def _remove_end_of_sentence(self, tweet):
        tweet = re.sub('<s>', " ", tweet)
        tweet = re.sub('</s>', " ", tweet)
        tweet = " ".join(tweet.split())
        return tweet

    def process_tweet(self, tweet_text):
        tweet_text_preprocessed = self._preprocess_tweet(tweet_text)
        tweet_tokenized = self.tknzr.tokenize(tweet_text_preprocessed)
        tweet_text_tokenized = " ".join(tweet_tokenized)
        clean_tweet = self._remove_end_of_sentence(tweet_text_tokenized)
        clean_tweet = clean_tweet.encode('utf-8')
        return clean_tweet