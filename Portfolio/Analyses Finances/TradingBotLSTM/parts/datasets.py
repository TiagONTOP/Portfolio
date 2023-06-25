#pip install --upgrade --no-cache-dir git+https://github.com/danilobaptistads/TvDataFeed-2.1.0
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

tv=TvDatafeed()

class GetCleanDatas:
    
    def __init__(self, interval):

        self.interval = interval

    def get_clean_mt5_data(self, tickers, n_bars):

        dict_interval = {
            '1D': mt5.TIMEFRAME_D1,
            '4H': mt5.TIMEFRAME_H4,
            '1H': mt5.TIMEFRAME_H1,
            '30M': mt5.TIMEFRAME_M30,
            '15M': mt5.TIMEFRAME_M15,
            '10M': mt5.TIMEFRAME_M10,
            '5M': mt5.TIMEFRAME_M5,
            '1M': mt5.TIMEFRAME_M1
        }
        
        datas = []
        for ticker in tickers:
            
            data = pd.DataFrame(mt5.copy_rates_from(ticker, dict_interval[self.interval], datetime.now(), n_bars))
            data['time'] = pd.to_datetime(data['time'], unit='s')
            data['symbol'] = np.full(shape=len(data), fill_value=ticker)
            data = data.drop(['real_volume'], axis=1)
            datas.append(data)
        
        data = pd.concat(datas, axis=0)
        data = data.set_index(['symbol', 'time'])
        return data
    
    def get_clean_tv_data(self, tickers, n_bars):

        
        dict_interval = {
            '1D': Interval.in_daily,
            '4H': Interval.in_4_hour,
            '1H': Interval.in_1_hour,
            '30M': Interval.in_30_minute,
            '15M': Interval.in_15_minute,
            '10M': Interval.in_15_minute,
            '5M': Interval.in_5_minute,
            '1M': Interval.in_1_minute
        }

        datas = []
        for ticker in tickers:
            exchange = tv.search_symbol(ticker)[0]['exchange']
            data = tv.get_hist(ticker, exchange, dict_interval[self.interval], n_bars=n_bars)
            data['symbol'] = data['symbol'].str.replace('{}:'.format(exchange), '')
            data.index.name = 'time'
            data = data.reset_index()
            datas.append(data)
        
        data = pd.concat(datas, axis=0)
        data = data.set_index(['symbol', 'time'])
        return data


class RNNDatas(GetCleanDatas):
    
    def __init__(self, rnn_lag, train_lenght, test_lenght, tickers, interval='4H'):
        super().__init__(interval)
        self.train_lenght = train_lenght
        self.test_lenght = test_lenght
        self.rnn_lag = rnn_lag
        self.tickers = tickers

    def get_returns(self, data):
        
        returns = (data
                   .groupby(level=0, group_keys=False)
                   .apply(lambda x: np.log(x.close/x.close.shift(1)))
                   .to_frame()
                   .rename(columns={'close' : 'returns'}))
        
        df_list = [returns]
        
        for lag in range(1, self.rnn_lag + 1):
            
            df_list.append(returns
                           .groupby(level=0, group_keys=False)
                           .apply(lambda x: x.returns.shift(lag))
                           .rename(f'returns_lag{lag}'))
            
        returns = pd.concat(df_list, axis=1)
            
        returns.dropna(how='any', inplace=True)
        
        return returns
    
    
    def create_multivariate_rnn_data(self, data):
        
        returns = self.get_returns(data)
        returns = returns.unstack(0).fillna(method='ffill').dropna().stack(level=1).swaplevel(0).sort_index()
        self.index_date = returns.index.get_level_values(1).unique()
        y = []
        X = []
        index_converter = {}
        for index, tick in enumerate(returns.index.levels[0]):
            
            index_converter[index] = tick
            y.append(np.array(returns.loc[tick].returns))
            X.append(np.array(returns.loc[tick].drop(['returns'], axis=1)))

        X = np.swapaxes(np.array(X).T, 0, 1)
        y = np.array(y).T
        self.index_converter = index_converter
        return X, y
    
    def get_train_data(self):
        n_bars = self.train_lenght + self.rnn_lag + 1
        data = self.get_clean_mt5_data(tickers=self.tickers, n_bars=n_bars)
        return self.create_multivariate_rnn_data(data)
    
    def get_predict_data(self):
        n_bars = self.test_lenght + self.rnn_lag + 1
        data = self.get_clean_mt5_data(tickers=self.tickers, n_bars=n_bars)
        X, y = self.create_multivariate_rnn_data(data)
        X = np.concatenate([np.delete(X, 0, axis=1), y.reshape(1, y.shape[0], y.shape[1])], axis=1)
        return X
    
    @property
    def get_index_to_ticker(self):
        return self.index_converter
    
    @property
    def get_index_date(self):
        return self.index_date


class GetMultivariateDatas(GetCleanDatas):

    def __init__(self, train_lenght, test_lenght, tickers_endog, tickers_exog, interval='4H'):
        super().__init__(interval)
        self.train_lenght = train_lenght
        self.test_lenght = test_lenght
        self.tickers_endog = tickers_endog
        self.tickers_exog = tickers_exog

    def get_multivariate_data(self, n_bars):
        change = 5
        data_endog = self.get_clean_mt5_data(tickers=self.tickers_endog, n_bars=n_bars).close.unstack(0)
        data_exog = self.get_clean_tv_data(tickers=self.tickers_exog, n_bars=n_bars).close.unstack(0)
        returns_endog = data_endog.pct_change().shift(-1).dropna()
        lags = list(range(5, 55, 5))
        columns_exog = data_exog.columns
        returns_exog = data_exog.pct_change(change).dropna()
        for lag in lags:
            returns_exog[[f'{c}_lag_{lag}' for c in columns_exog]] = returns_exog[list(columns_exog)].copy().shift(lag)
        returns_exog = returns_exog.resample('H', label='right').last().fillna(method='ffill').dropna()

        return returns_exog, returns_endog
    
    def get_train_data(self):

        n_bars = self.train_lenght + 50 + 1
        returns_exog, returns_endog = self.get_multivariate_data(n_bars)
        X_columns = returns_exog.columns
        y_columns = returns_endog.columns
        data = pd.concat([returns_endog, returns_exog], axis=1, join='inner').dropna()
        X = data[X_columns]
        y = data[y_columns]
        return X, y
    
    def get_predict_data(self):

        n_bars = self.test_lenght + 50 + 1
        returns_exog, _ = self.get_multivariate_data(n_bars)
        X = returns_exog.iloc[-self.test_lenght:]

        return X
    
class GetMAData(GetCleanDatas):

    def __init__(self, test_lenght, train_lenght, tickers, interval='4H'):

        super().__init__(interval)
        self.test_length = test_lenght
        self.train_lenght = train_lenght
        self.tickers = tickers

    def get_ma_datas(self, n_bars):

        data = self.get_clean_mt5_data(n_bars=n_bars, tickers=self.tickers)
        returns = data.groupby(level=0, group_keys=False).apply(lambda x: x.close.pct_change().shift(-1))
        lags = list(range(5, 200, 20))
        for i, lag in enumerate(lags, start=1):
            if i == 1:
                
                mas = data.groupby(level='symbol', group_keys=False, as_index=False)['close'].rolling(lag).mean().drop(['symbol'], axis=1)
                mas.columns = [f'lag_{lag}']
            
            else:
                
                mas[f'ma_{lag}'] = data.groupby(level='symbol', group_keys=False, as_index=False)['close'].rolling(lag).mean().drop(['symbol'], axis=1)
        
        changes = mas.groupby(level='symbol', group_keys=False).apply(lambda x: x.pct_change())
        changes.index.names = ['symbol', 'date']
        returns.index.names = ['symbol', 'date']
        return changes, returns
    
    def get_train_data(self):

        n_bars = self.train_lenght + 200
        changes, returns = self.get_ma_datas(n_bars=n_bars)
        data = changes.join(returns).rename({'close': 'target'}, axis=1).dropna()
        X = data.drop(['target'], axis=1)
        y = data['target']
        return X, y
    
    def get_predict_data(self):

        n_bars = self.test_length + 200
        X, _  = self.get_ma_datas(n_bars=n_bars)
        X = X.groupby(level=0, group_keys=False).apply(lambda x: x.iloc[-self.test_length:])
        return X
    











