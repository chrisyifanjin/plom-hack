import numpy as np
import pickle
import gzip
from sklearn import datasets, metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from django.conf import settings

"""
Train a digit classifier
"""


class MachineLearningException(Exception):
    pass


def train_knn_classifier(n: int, save_filename: str):
    """Train a toy KNN classifier on digit recognizing data, save training data and trained model to disk"""
    ml_data_path = settings.MEDIA_ROOT / 'ml_huey'

    if not ml_data_path.exists():
        raise FileNotFoundError(f'Data path {ml_data_path} not found.')

    digits_data, digits_target = datasets.fetch_openml("mnist_784", return_X_y=True, as_frame=False, data_home=ml_data_path)
    X_train, X_test, y_train, y_test = train_test_split(digits_data, digits_target, test_size=0.2, train_size=0.1)

    print("Training K-Nearest-Neighbors classifier")
    
    model = KNeighborsClassifier(n_neighbors=n)
    model.fit(X_train, y_train)

    train_sys = model.predict(X_train)
    train_acc = np.mean(train_sys == y_train)
    print("Train accuracy: {:.2f}".format(train_acc))

    with gzip.open(save_filename, "wb") as f:
        save_dict = {'model': model, 'X_test': X_test, 'y_test': y_test}
        pickle.dump(save_dict, f)

    return train_acc


def test_knn_classifier(model_path):
    """Load a trained model and find its test accuracy"""
    if not model_path.exists():
        raise FileNotFoundError(f'Model path {model_path} not found.')

    saved_dict = pickle.load(model_path)
    model = saved_dict['model']
    X_test = saved_dict['X_test']
    y_test = saved_dict['y_test']

    test_sys = model.predict(X_test)
    test_acc = np.mean(test_sys == y_test)

    return test_acc
