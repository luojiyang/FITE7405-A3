import numpy as np
from scipy.stats import norm


# F(sigma) function
def f_sigma(sigma,S, K, r, T, V, option_type):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / sigma * np.sqrt(T)
    d2 = d1 - sigma * np.sqrt(T)
    if (option_type == 'call'):
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2) - V
    elif (option_type == 'put'):
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) - V
    return None

# F'(sigma) function
def f_prime_sigma(sigma, S, K, r, T):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / sigma * np.sqrt(T)
    return S * np.sqrt(T) * norm.pdf(d1)

# Newton method to find the implied volatility
def impliedVolatility(S, K, r, T, V, option_type):
    '''
    Calculate the implied volatility of an option using the Newton method.

    S: current stock price
    K: strike price
    r: risk-free rate
    T: maturity time
    V: option price
    option_type: 'call' or 'put'
    '''
    sigmahat = np.sqrt(2 * abs((np.log(S / K) + r * T) / T))
    tol = 1e-8
    nmax = 100
    sigmadiff = 1
    n = 1
    sigma = sigmahat
    while sigmadiff > tol and n < nmax:
        sigma_delta = f_sigma(sigma, S, K, r, T, V, option_type) / f_prime_sigma(sigma, S, K, r, T)
        sigma = sigma - sigma_delta
        sigmadiff = abs(sigma_delta)
        n = n + 1
    
    return sigma