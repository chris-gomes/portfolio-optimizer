import numpy as np
import pandas as pd

from scipy.optimize import minimize

class PortfolioOptimizer():

    # creates optimizer by taking in monthly stock returns and risk free returns
    def __init__(self, stock_returns, rf_rates):
        if not isinstance(stock_returns, pd.DataFrame):
            raise ValueError('stock_returns must be a pandas data frame')
        elif not isinstance(rf_rates, np.ndarray):
            raise Exception('rf_rates must be a numpy array')
        elif rf_rates.size != stock_returns.shape[0]:
            raise Exception('stock_returns and rf_rates must have the same number of rows')
        else:
            self.stock_returns = stock_returns
            self.rf_rates = rf_rates

    def is_valid_weights(self, weights):
        if weights == None:
            raise ValueError('weights cannot be None')
        elif type(weights) != list:
            raise ValueError('weights must be a list')
        elif len(weights) != self.stock_returns.shape[1]:
            raise ValueError('weights must be the same length as the number of stocks')
        elif np.sum(weights) != 1:
            raise ValueError('weights must sum up to 1')
        else:
            return True

    # Define the portfolio returns function
    def port_ret(self, weights):
        if self.is_valid_weights(weights):
            return np.sum(self.stock_returns.mean()*weights*12)

    # Define the portfolio standard deviation function
    def port_sd(self, weights):
        if self.is_valid_weights(weights):
            weights_array = np.array(weights)
            return np.sqrt(np.dot(weights_array.T, np.dot(self.stock_returns.cov()*12, weights)))

    # Define the negative Sharpe Ratio function that we will minimize
    def neg_SR(self, weights):
        sharpe_ratio = (self.port_ret(weights) - self.rf_rates['rf'].mean() * 12) / self.port_sd(weights)
        return -1 * sharpe_ratio

    # find the portfolio with the largest Sharpe ratio
    def find_optimal_port(self, weights):
        constraints = ({'type':'eq','fun': lambda weights: np.sum(weights) - 1})

        # initialize bounds for weights
        bounds = [(0, 1)] * len(weights)

        # create an intial guess of equal weights
        
        init_guess = [1]

        # Use the SLSQP (Sequential Least Squares Programming) for minimization
        optimal_port = minimize(self.neg_SR,init_guess,method='SLSQP',bounds = bounds, constraints=constraints)