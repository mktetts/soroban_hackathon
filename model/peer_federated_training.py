import sys
sys.path.append('../consensus/')

import numpy as np
import warnings

warnings.filterwarnings('ignore')

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import datasets
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score


import consensus as Con


con = Con.Consensus()


class LogisticRegression():

    def __init__(self, lr=0.001, n_iters=1000, mod=1):
        self.lr = lr
        self.n_iters = n_iters
        self.weights = None
        self.bias = None
        self.mod = mod

    def fit(self, X, y, weights, bias):
        n_samples, n_features = X.shape
        if weights != None:
            self.weights = weights
        else:
            self.weights = np.zeros(n_features)
        if bias != None:
            self.bias = bias
        else:
            self.bias = 0
        self.weights = con.encrypt(self.weights, mod=self.mod)
        self.bias = con.encrypt(self.bias, mod = self.mod)
        # print(self.weights, self.bias)
        for _ in range(self.n_iters):
            linear_pred = "np.dot(X, weights) + bias"
            linear_pred = con.evaluate(linear_pred, values={'nenc' : {'X' : X, 'np' : np}, 'enc': {'weights' : self.weights, 'bias' : self.bias}})

            # predictions = sigmoid(linear_pred)
            # predictions = con.evaluate(linear_pred, v)
            
            sigmoid = "np.maximum(0, x)"
            predictions = con.evaluate(sigmoid, values = {'nenc' : {'np' : np}, 'enc': {'x' : linear_pred}})
            # predictions = sigmoid(linear_pred)

            n = (1 / n_samples)

            dw = "n * np.dot(X, (predictions - y))"
            dw = con.evaluate(dw, values={'nenc' : {'n' : n, 'X' : X.T, 'y' : y, 'np' : np}, 'enc' : { 'predictions' : predictions}})
            db = "n * np.sum(predictions-y)"
            db = con.evaluate(db, values={'nenc' : {'n' : n, 'y' : y, 'np' : np}, 'enc' : { 'predictions' : predictions}})
            exp = "[w - (value['lr'] * d) for w, d in zip(value['weights'], value['dw'])]"
            self.weights = con.evaluate(exp, values={'nenc' : {'lr' : self.lr}, 'enc' : {'weights' : self.weights, 'dw' : dw}}, cal="norm")
        #     self.bias = self.bias - self.lr*db
            # print("self.bias", self.bias)
            # print("self.db", db)
            exp = "bias - lr * db"
            self.bias = con.evaluate(exp, values={'nenc' : {'lr' : self.lr}, 'enc' : {'bias' : self.bias, 'db' : db}})


    def predict(self, X):
        linear_pred = "np.dot(X, weights) + bias"
        linear_pred = con.evaluate(linear_pred, values={'nenc' : {'X' : X, 'np' : np}, 'enc': {'weights' : self.weights, 'bias' : self.bias}})

        # y_pred = sigmoid(linear_pred)
        sigmoid = "np.maximum(0, x)"
        y_pred = con.evaluate(sigmoid, values = {'nenc' : {'np' : np}, 'enc': {'x' : linear_pred}})

        # y_pred = sigmoid(linear_pred)

        # class_pred = [0 if y<=0.5 else 1 for y in y_pred]
        exp = "[0 if y<=0.5 else 1 for y in y_pred]"
        class_pred = con.evaluate(exp, values={'enc' : {'y_pred' : y_pred}})
        return class_pred
    

def start_train(X, y, mod):
    mask = (X['Age']).mean()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234)
    clf = LogisticRegression(lr=0.01, n_iters=1000, mod=mod)
    clf.fit(X_train,y_train, None, None)
    y_pred = clf.predict(X_test)
    print("\n\n\t\t******** Training Started *******\n\n")
    def accuracy(y_pred, y_test):
        exp = "np.sum(y_pred==y_test)/len(y_test)"
        return con.evaluate(exp, values={'nenc' : {'y_test' : y_test, 'np' : np}, 'enc' : {'y_pred' : y_pred}})
    acc = accuracy(y_pred, y_test)
    print("decrypted_acc : ", con.decrypt(acc))
    return {'accuracy' : acc, "decrypted_acc" : con.decrypt(acc), 'weights' : clf.weights, 'bias' : clf.bias, 'mask' : mask}


def overall_accuracy(X, weights, bias):
    linear_pred = np.dot(X, weights) + bias

    y_pred = np.maximum(0, linear_pred)
    # print(y_pred)

# Reshape the array into a one-dimensional array
    
    class_pred = [0 if y<=0.5 else 1 for y in y_pred]
    return class_pred