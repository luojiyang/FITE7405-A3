import numpy as np
from scipy.stats import norm


# formula for Black-Scholes model - call option
def cutValueByBlackScholes(S, K, T, r, d1, d2):
    """
    Calculate the value of a European call option using the Black-Scholes formula.

    S: current stock price
    K: strike price
    t: current time
    T: maturity time
    sigma: volatility
    r: risk-free rate
    d1: d1
    d2: d2
    """

    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


# formula for Black-Scholes model - put option
def putValueByBlackScholes(S, K, T, r, d1, d2):
    """
    Calculate the value of a European put option using the Black-Scholes formula.

    S: current stock price
    K: strike price
    t: current time
    T: maturity time
    sigma: volatility
    r: risk-free rate
    d1: d1
    d2: d2
    """
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


# formula for Black-Scholes model
def valueByBlackScholes(S, K, T, sigma, r, optionType):
    """
    Calculate the value of a European option using the Black-Scholes formula.

    S: current stock price
    K: strike price
    t: current time
    T: maturity time
    sigma: volatility
    r: risk-free rate
    optionType: 'call' or 'put'
    """
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if optionType == "call":
        return cutValueByBlackScholes(S, K, T, r, d1, d2)
    elif optionType == "put":
        return putValueByBlackScholes(S, K, T, r, d1, d2)
    else:
        return "Invalid option type"
