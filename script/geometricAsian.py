import numpy as np
from scipy.stats import norm


def geoAsianCall(S, K, T, d1_hat,d2_hat,miu_hat, r):
    """
    Closed-form formulas for geometric Asian call

    S: spot price of asset S(0)
    K: strike price
    T: maturity time
    d1_hat: d1_hat
    d2_hat: d2_hat
    miu_hat: drift
    r: risk-free rate
    """
    return np.exp(-r * T) * (
        S * np.exp(miu_hat * T) * norm.cdf(d1_hat) - K * norm.cdf(d2_hat)
    )


def geoAsianPut(S, K, T, d1_hat,d2_hat,miu_hat, r):
    """
    Calculate the value of a European put option using the Black-Scholes formula.

    S: spot price of asset S(0)
    K: strike price
    T: maturity time
    d1_hat: d1_hat
    d2_hat: d2_hat
    miu_hat: drift
    r: risk-free rate
    """
    
    return np.exp(-r * T) * (
        K * norm.cdf(-d2_hat) - S * np.exp(miu_hat * T) * norm.cdf(-d1_hat)
    )


def geoAsian(S, K, T, sigma, r, n, optionType):
    """
    Calculate the value of a European option using the Black-Scholes formula.

    S: spot price of asset S(0)
    K: strike price
    T: maturity time
    sigma: volatility
    r: risk-free rate
    n: number of steps
    optionType: 'call' or 'put'
    """
    sigma_hat = sigma * np.sqrt((n + 1) * (2 * n + 1) / (6 * n**2))
    miu_hat = (r - 0.5 * sigma**2) * (n + 1) / (2 * n) + 0.5 * sigma_hat**2
    d1_hat = (np.log(S / K) + (miu_hat + 0.5 * sigma_hat**2) * T) / (
        sigma_hat * np.sqrt(T)
    )
    d2_hat = d1_hat - sigma_hat * np.sqrt(T)
    if optionType == "call":
        return geoAsianCall(S, K, T, d1_hat,d2_hat,miu_hat, r)
    elif optionType == "put":
        return geoAsianPut(S, K, T, d1_hat,d2_hat,miu_hat, r)
    else:
        return "Invalid option type"
