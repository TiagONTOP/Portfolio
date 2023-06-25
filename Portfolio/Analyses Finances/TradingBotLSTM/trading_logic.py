import numpy as np
import pandas as pd
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, 'parts'))
from broker import PyRobot
from datasets import RNNDatas, GetMultivariateDatas, GetMAData, GetCleanDatas
from models import MultivariateLSTM, MultivariateLinearRegression, MaRidge, rsi_signal, interest_rates_signal


login_mt5 = 1051711759
mdp_mt5 = 'SYEHFG2C9B'
server = 'FTMO-Demo'
leverage = 8.511402089138556
last_time = str()
tickers_to_trades = ['GBPJPY', 'GBPUSD', 'EURGBP', 'EURUSD', 'USDCAD', 'USDJPY']

# RNN Variables
rnn_lag = 300
rnn_test_lenght = 1
rnn_train_lenght = 2000
rnn_tickers = ['AUDCAD', 'AUDJPY', 'AUDNZD', 'AUDCHF', 'AUDUSD', 'GBPAUD', 
                'GBPCAD', 'GBPJPY', 'GBPNZD', 'GBPCHF', 'GBPUSD', 'CADJPY',
                'CADCHF', 'EURAUD', 'EURGBP', 'EURCAD', 'EURJPY', 'EURCHF', 
                'EURUSD', 'EURNZD', 'NZDCAD', 'NZDCHF', 'NZDUSD', 'NZDJPY',
                'CHFJPY', 'USDCAD', 'USDCHF', 'USDJPY']
rnn_count_predict = 500

rnndata = RNNDatas(rnn_lag=rnn_lag, train_lenght=rnn_train_lenght, test_lenght=rnn_test_lenght, tickers=rnn_tickers)
lstm = MultivariateLSTM(rnn_tickers)


# Multivariate Datas

multi_test_lenght = 1
multi_train_lenght = 2000
tickers_enog = ['GBPJPY', 'GBPUSD', 'EURGBP', 'EURUSD', 'USDCAD', 'USDJPY']
tickers_exog = ['NG1!', 'CL1!', 'GC1!', 'HG1!', 'SI1!', 'ZC1!', 'ZS1!', 'ZW1!']
multi_count_predict = 200
multidata = GetMultivariateDatas(train_lenght = multi_train_lenght, test_lenght = multi_test_lenght, tickers_endog = tickers_enog, tickers_exog = tickers_exog)
multivariatelr = MultivariateLinearRegression()


# MA Data

ma_test_lenght = 1
ma_train_lenght =  2000
ma_tickers = ['AUDCAD', 'AUDJPY', 'AUDNZD', 'AUDCHF', 'AUDUSD', 'GBPAUD', 
            'GBPCAD', 'GBPJPY', 'GBPNZD', 'GBPCHF', 'GBPUSD', 'CADJPY',
            'CADCHF', 'EURAUD', 'EURGBP', 'EURCAD', 'EURJPY', 'EURCHF', 
            'EURUSD', 'EURNZD', 'NZDCAD', 'NZDCHF', 'NZDUSD', 'NZDJPY',
            'CHFJPY', 'USDCAD', 'USDCHF', 'USDJPY']
ma_count_predict = 30

madata = GetMAData(test_lenght = ma_test_lenght, train_lenght = ma_train_lenght, tickers = ma_tickers)
ridge = MaRidge()



# rates

rates_tickers = ['EU02Y', 'US02Y', 'GB02Y', 'CA02Y', 'JP02Y']

# rsi

rsi_tickers = ['GBPJPY', 'GBPUSD', 'EURGBP', 'EURUSD', 'USDCAD', 'USDJPY']

cleandata = GetCleanDatas(interval='4H')

brk = PyRobot(client_id=login_mt5, client_mdp=mdp_mt5, trading_serveur=server, leverage=leverage, tickers=tickers_to_trades)
brk._create_session()



if __name__ == '__main__':

    while True:

        actual_time = cleandata.get_clean_mt5_data(['EURUSD'], n_bars=1)
        actual_time = str(actual_time.index.levels[1][0])
        logic_cond = [actual_time != '?ILUHOI', brk.market_open]

        if all(logic_cond):
            
            # Train model
            loopmodel = [lstm, multivariatelr, ridge]
            loopdata = [rnndata, multidata, madata]
            loopcount = [rnn_count_predict, multi_count_predict, ma_count_predict]
            for dataset, model, count in zip(loopdata, loopmodel, loopcount):
                if model.count_predict >= count:
                    X, y = dataset.get_train_data()
                    model.train_model(X, y)

            # Predictions
            
            listkeys = ['lstm', 'commodities', 'ma_ridge']
            dictpreds = dict()
            for dataset, model, key in zip(loopdata, loopmodel, listkeys):
                X = dataset.get_predict_data()
                dictpreds[key] = model.predict(index_to_ticker=dataset.get_index_to_ticker, X=X).loc[tickers_to_trades] if key == 'lstm' else model.predict(X).loc[tickers_to_trades]
            
            ratesdata = cleandata.get_clean_tv_data(tickers=rates_tickers, n_bars=5)
            rsidata = cleandata.get_clean_mt5_data(tickers=rsi_tickers, n_bars=16)
            dictpreds['rsi'] = rsi_signal(rsidata)
            dictpreds['rates'] = interest_rates_signal(ratesdata)
            dictweights = {

                'lstm': 0.244452,
                'rsi' : 0.165001,
                'rates': 0.296181,
                'ma_ridge': 0.135404,
                'commodities': 0.158963
            }
            listconcat = list()
            for key in dictweights.keys():
                listconcat.append(dictpreds[key] * dictweights[key])
            
            finalpreds = dict(np.sign(pd.concat(listconcat, axis=1, join='inner').sum(axis=1)))

            # close positions

            brk.create_close_trades(finalpreds)

            # open orders
            # ajouter une fonction de verification dans create entry trades pour savoir si le ticker est deja dans le portfolio
            # verifier le leviers car ici on trades un porteufeille et plus une seule paire

            brk.create_entry_trades(finalpreds)
            last_time = cleandata.get_clean_mt5_data(['EURUSD'], n_bars=1)
            last_time = str(last_time.index.levels[1][0])