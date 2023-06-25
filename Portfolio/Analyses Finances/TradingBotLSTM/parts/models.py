import pandas as pd
import numpy as np
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop, Adagrad, Adamax, Adam
import tensorflow as tf
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from talib import RSI




class MultivariateLSTM:

    def __init__(self, tickers, count_predict=500):
        
        self.model = Sequential([
                                LSTM(units=128,
                                    input_shape=(300, len(tickers)), name='LSTM'),
                                Dense(len(tickers), name='Output')
                            ])
        self.count_predict = count_predict

    def train_model(self, X, y):
        
        X *= 1000
        y *= 1000
        self.model.compile(loss=tf.keras.losses.MeanAbsoluteError(), optimizer=Adamax(learning_rate=0.1))
        self.model.fit(X, y, epochs=1, batch_size=64, shuffle=False)
        self.count_predict = 0
    
    def predict(self, index_to_ticker, X):
        
        yhat = self.model.predict(X)
        dict_pred = dict()
        for i in range(yhat.shape[1]):
            dict_pred[index_to_ticker[i]] = 1 if yhat[-1, i] > 0 else -1

        self.count_predict += 1
        
        return pd.Series(dict_pred)
    

class MultivariateLinearRegression:

    def __init__(self, count_predict=200):

        lr = LinearRegression()
        pipe = Pipeline([('scaler', StandardScaler()), ('model', lr)])
        self.model = MultiOutputRegressor(pipe)
        self.count_predict = count_predict

    def train_model(self, X, y):

        X *= 100
        y *= 100

        self.model.fit(X, y)
        self.count_predict = 0
        self.ycolumns = y.columns

    def predict(self, X):

        X *= 100
        yhat = pd.Series(np.where(self.model.predict(X)[0] > 0, 1, -1), index=self.ycolumns)
        self.count_predict += 1

        return yhat
    

class MaRidge():

    def __init__(self, count_predict=30):

        self.model = Pipeline([('scaler', StandardScaler()), ('Ridge', Ridge(alpha=1))])
        self.count_predict = 30


    def train_model(self, X, y):

        self.model.fit(X, y)
        self.count_predict = 0
        self.yindex= list(y.index.levels[0])

    def predict(self, X):
        self.count_predict += 1
        return pd.Series(np.where(self.model.predict(X) > 0, 1, -1), index=self.yindex)
    

def rsi_signal(data):
    X = data.close.groupby(level=0).apply(lambda x: x.iloc[-15:])
    rsi = X.groupby(level=0 ,group_keys=False).apply(lambda x: RSI(x)[-1])
    rsi = pd.Series(np.where(rsi > 50.42, -1, 1), index=rsi.index)
    return rsi

def interest_rates_signal(data):

    data = data.close

    spreads = {
        'GBPJPY': ['GB02Y', 'JP02Y'], 
        'GBPUSD': ['GB02Y', 'US02Y'], 
        'EURGBP': ['EU02Y', 'GB02Y'], 
        'EURUSD': ['EU02Y', 'US02Y'], 
        'USDCAD': ['US02Y', 'CA02Y'], 
        'USDJPY': ['US02Y', 'JP02Y']
    }

    signals = dict()

    for key in spreads.keys():

        first = data[spreads[key][0]][-1]
        second = data[spreads[key][1]][-1]
        
        spread = first - second
        signal = 1 if spread > 0 else -1
        signals[key] = signal
    return pd.Series(signals)