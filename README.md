## Fraud News Classifier
---
The aim of the project is to detect fraud-related news from all the news published overnight on [stocklabs](https://stocklabs.com/news)
 

**Installation**

Just clone the repo and download the necessary libraries
```sh
$ git clone +https://github.com/bordbe/fraudnews
$ cd fraudnews
$ pip install -r requirements.txt
```

**Class Prediction**

The classification follows a two-steps process:

1) SVM classifier with Word2Vec vectorizer
2) Sentiment analysis with VADER
 
In deed, we perform a sentiment analysis on the headlines classified as fraud et we keep the ones with a negative score above 0. 

To do it, just run:
```sh
$ python classifier.py
```

