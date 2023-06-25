import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


class FTMOLeverageOptimazation:


    def __init__(self, sigma, mu, n_sim, S0):

        self.sigma = sigma
        self.mu = mu
        self.n_sim = n_sim
        self.S0 = S0

    def get_gbms(self, time_in_month, leverage):
        days = 252
        months = 22
        dt = 1/days
        sigma = self.sigma * leverage
        mu = self.mu * leverage
        n_sim = self.n_sim
        S0 = self.S0
        gbm = np.full(shape=(time_in_month * months, n_sim), fill_value=S0)
        for i in range(1, gbm.shape[0]):
            gbm[i] = gbm[i-1] * np.exp((mu - sigma**2/2) * dt + sigma * np.sqrt(dt) * np.random.standard_normal(size=(n_sim,)))
        return gbm
        
    def get_probas(self, leverage, time_in_month, target, dd_max):
        

        gbm = self.get_gbms(time_in_month, leverage=leverage[0])
        returns = np.diff(gbm, axis=0)/gbm[:-1]
        dd_gbm = np.zeros(shape=returns.shape)
        pass_fails = []
        min_time = 10
        thr_target = self.S0 * (1 + target)
        
        # Calculation of draw-downs

        for i in range(returns.shape[0]):
            if i == 0:
                dd_gbm[i] = np.where(returns[i] < 0, returns[i], 0)
            else:
                dd = (1 + dd_gbm[i-1]) * (1 + returns[i]) - 1
                dd_gbm[i] = np.where(dd < 0, dd, 0)

        dd_gbm = np.abs(dd_gbm)

        # Calculation of probabilities to pass FTMO first test

        for i in range(gbm.shape[1]):
    
            if dd_gbm[:, i][dd_gbm[:, i] > dd_max].any():
                pass_fails.append(0)
            elif gbm[min_time-1:, i][gbm[min_time-1:, i]>thr_target].any():
                pass_fails.append(1)
            else:
                pass_fails.append(0)

        return np.mean(pass_fails)
    
    def objective(self, leverage, time_in_month, target, dd_max):
        return  - self.get_probas(leverage, time_in_month, target, dd_max)
    
    
    def optimize_leverage(self):

        bounds = [(0, None)]
        time_in_month_first = 1
        target_first = 0.10
        dd_max = 0.10
        x0 = [1.]
        res1 = minimize(self.objective, x0=x0, args=(time_in_month_first, target_first, dd_max), method='Powell', bounds=bounds)
        self.first_best_leverage = res1.x[0]
        self.first_best_proba = -res1.fun
        time_in_month_second = 2
        target_second = 0.05
        res2 = minimize(self.objective, x0=x0, args=(time_in_month_second, target_second, dd_max), method='Powell', bounds=bounds)
        self.second_best_leverage = res2.x[0]
        self.second_best_proba = -res2.fun
        self.total_proba = res1.fun * res2.fun

        






