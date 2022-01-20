import argparse
import json
import pickle
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from scipy.sparse import csr_matrix
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score


def get_X_y(data: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    data['category'] = data['category'].apply(lambda x: 1 if x == 'clickbait' else 0)
    X, y = data.drop('category', axis=1), data['category'].to_numpy()
    return X, y


def tfidf_preprocess(X_train: pd.DataFrame, X_test: Optional[pd.DataFrame] = None) -> Tuple[csr_matrix, csr_matrix]:
    stop_words = set(stopwords.words("english"))
    tfidf = TfidfVectorizer(stop_words=stop_words, ngram_range=(1, 2))
    tfidf_X_train = tfidf.fit_transform(X_train)
    tfidf_X_test = tfidf.transform(X_test)
    return tfidf_X_train, tfidf_X_test


def read_prepare_data(train_data: pd.DataFrame,
                      test_data: pd.DataFrame) -> Tuple[csr_matrix, csr_matrix, np.ndarray, np.ndarray]:
    X_train, y_train = get_X_y(train_data)
    X_test, y_test = get_X_y(test_data)
    X_train, X_test = tfidf_preprocess(X_train.headline, X_test.headline)
    return X_train, X_test, y_train, y_test


def train_model(X_train: csr_matrix, y_train: np.ndarray) -> ClassifierMixin:
    classifier = RandomForestClassifier(class_weight='balanced')
    classifier.fit(X_train, y_train)
    return classifier


def test_model(classifier: ClassifierMixin, X_test: csr_matrix, y_test: np.ndarray) -> Tuple[float, float]:
    test_preds = classifier.predict(X_test)
    accuracy = accuracy_score(y_test, test_preds)
    f1 = f1_score(y_test, test_preds)
    return accuracy, f1


def write_result(output_file_path: str, accuracy: float, f1: float):
    with open(output_file_path, 'w') as output_file:
        json.dump({'accuracy': accuracy, 'f1_score': f1}, output_file)


def save_model(classifier: ClassifierMixin, model_path: str):
    with open(model_path, 'wb') as f:
        pickle.dump(classifier, f)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Concatenate two datasets.')
    parser.add_argument('--train_data', nargs='+', type=str, required=True,
                        help='Path to datasets. Concats into one if multiple')
    parser.add_argument('--test_data', nargs='+', type=str, required=True,
                        help='Path to a test dataset. Concats into one if multiple')
    parser.add_argument('--results_path', type=str, required=True, help='Path to store metrics on test dataset')
    parser.add_argument('--model_path', type=str, help='Path to store trained model')
    args = parser.parse_args()

    train_data = pd.concat([pd.read_csv(path) for path in args.train_data])
    test_data = pd.concat([pd.read_csv(path) for path in args.train_data])

    X_train, X_test, y_train, y_test = read_prepare_data(train_data, test_data)

    classifier = train_model(X_train, y_train)
    if args.model_path:
        save_model(classifier, args.model_path)

    accuracy, f1 = test_model(classifier, X_test, y_test)
    write_result(args.results_path, accuracy, f1)
