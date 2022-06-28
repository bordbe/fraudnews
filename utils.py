import re
import string
import nltk
import os
import sys
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
wl = WordNetLemmatizer()
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        self.dim = len(next(iter(word2vec.values())))

    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])


def preprocess(text):
    """preprocess news headlines before feeding them into the classifier"""
    text = text.lower()
    text = text.strip()
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub('[^a-zA-Z]', ' ', text)  # keep only alphabet characters
    text = re.compile('<.*?>').sub('', text)
    text = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', text)
    text = re.sub('\s+', ' ', text)
    text = re.sub(r'\[[0-9]*\]', ' ', text)
    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
    text = re.sub(r'\d', ' ', text)
    text = re.sub(r'\s+', ' ', text)  # adjust white space
    return text


def stopword(string):
    """remove stopwords from string"""
    a = [i for i in string.split() if i not in stopwords.words('english')]
    return ' '.join(a)


def get_wordnet_pos(tag):
    """assign POS to wordnet"""
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def lemmatizer(string):
    """lemmatize headlines"""
    word_pos_tags = nltk.pos_tag(word_tokenize(string))  # Get position tags
    a = [wl.lemmatize(tag[0], get_wordnet_pos(tag[1])) for idx, tag in enumerate(
        word_pos_tags)]  # Map the position tag and lemmatize the word/token
    return " ".join(a)


def text_process(string):
    """preprocess text via calling necessary functions"""
    return lemmatizer(stopword(preprocess(string)))
