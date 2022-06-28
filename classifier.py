import os
import sys
import pickle
from os.path import dirname, join
import numpy as np
import pandas as pd
from datetime import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from scraper import get_overnight_news
from utils import text_process, MeanEmbeddingVectorizer
pd.options.mode.chained_assignment = None

PATH_VECTORIZER = join(dirname(__file__), "config", "word2vec.pkl")
PATH_CLASSIFIER = join(dirname(__file__), "config", "svm_model.pkl")


def set_up():
    """load the word2vec, classifier via the config file"""
    w2v = PATH_VECTORIZER
    classifier = PATH_CLASSIFIER
    w2v = pickle.load(open(w2v, "rb+"))
    classifier = pickle.load(open(classifier, "rb+"))
    return w2v, classifier


def classify_fraud(df_news):
    """classify the news"""
    w2v, classifier = set_up()
    X_tok = [nltk.word_tokenize(i) for i in df_news['clean_text']]
    X_vectors_w2v = w2v.transform(X_tok)
    return classifier.predict(X_vectors_w2v)


def sentiment_analysis(df_fraud):
    """perform sentiment analysis on the headlines"""
    new_words = {
        'fraud': -4.0,
        'corrupt': -4.0,
    }
    sia = SentimentIntensityAnalyzer()
    sia.lexicon.update(new_words)
    df_fraud.loc[:, "polarity"] = df_fraud.loc[:, "clean_text"].apply(
        lambda x: sia.polarity_scores(x))
    df_fraud.loc[:, ["neg", "neu", "pos", "compound"]
                 ] = df_fraud.loc[:, "polarity"].apply(pd.Series)
    df_fraud = df_fraud[df_fraud["neg"] > 0]
    return df_fraud[["text", "class", "neg", "neu", "pos"]].sort_values(by="neg", ascending=False)


def main():
    today = datetime.strftime(datetime.now(), format="%Y%m%d")
    print("============ START ============")
    df_news = get_overnight_news()
    print(f"Retrieved {len(df_news)} news")
    df_news['clean_text'] = df_news['text'].apply(
        lambda x: text_process(x))
    print("Headlines preprocessed")
    df_news["class"] = classify_fraud(df_news)
    df_news["class"] = np.where(
        df_news["class"] == 1, "fraud", "normal")
    df_fraud = df_news[df_news["class"] == "fraud"]
    print(f"Headlines classified, {len(df_fraud)} as fraud")
    df_sent = sentiment_analysis(df_fraud)
    print(
        f"Sentiment analysis performed, filtered {len(df_sent)} news as negative")
    today = datetime.strftime(datetime.now(), format="%Y%m%d")
    df_sent = df_sent.drop_duplicates(keep="last")
    excel_path = join(os.getcwd(), f"{today}_fraudnews.xlsx")
    df_sent.to_excel(excel_path)
    print(f"Successfully saved negative news file in {excel_path}")
    print("============ END ============")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
