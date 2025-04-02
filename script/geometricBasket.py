import numpy as np
from scipy.stats import norm


def geoBasketCall(d1_hat, d2_hat, B_g_0, miu_B_g, K, T, r):
    """
    Closed-form formulas for geometric Basket call

    d1_hat: d1_hat
    d2_hat: d2_hat
    B_g_0: level
    miu_B_g: drift
    K: strike price
    T: maturity time
    r: risk-free rate
    """

    return np.exp(-r * T) * (
        B_g_0 * np.exp(miu_B_g * T) * norm.cdf(d1_hat) - K * norm.cdf(d2_hat)
    )


def geoBasketPut(d1_hat, d2_hat, B_g_0, miu_B_g, K, T, r):
    """
    Closed-form formulas for geometric Basket put

    d1_hat: d1_hat
    d2_hat: d2_hat
    B_g_0: level
    miu_B_g: drift
    K: strike price
    T: maturity time
    r: risk-free rate
    """
    return np.exp(-r * T) * (
        K * norm.cdf(-d2_hat) - B_g_0 * np.exp(miu_B_g * T) * norm.cdf(-d1_hat)
    )


def geoBasket(S_1, S_2, K, T, sigma_1, sigma_2, r, pho,optionType):
    """
    Calculate the value of a European option using the Black-Scholes formula.

    S_1: spot price of asset S_1(0)
    s_2: spot price of asset S_2(0)
    K: strike price
    T: maturity time
    sigma_1: volatility of asset S_1
    sigma_2: volatility of asset S_2
    r: risk-free rate
    pho: correlation coefficient
    """
    if optionType not in ["call", "put"]:
        return "Invalid option type"
    B_g_0 = (S_1 * S_2) ** (1 / 2)
    sigma_B_g = (
        np.sqrt(2 * (sigma_1**2) + 2 * (sigma_2**2) + 2 * sigma_1 * sigma_2 * pho) / 2
    )
    miu_B_g = r - 0.5 * (sigma_1**2 + sigma_2**2) / 2 + 0.5 * sigma_B_g**2
    d1_hat = np.log(B_g_0 / K) + (miu_B_g + 0.5 * sigma_B_g**2) * T / (
        sigma_B_g * np.sqrt(T)
    )
    d2_hat = d1_hat - sigma_B_g * np.sqrt(T)
    if optionType == "call":
        return geoBasketCall(d1_hat, d2_hat, B_g_0, miu_B_g, K, T, r)
    elif optionType == "put":
        return geoBasketPut(d1_hat, d2_hat, B_g_0, miu_B_g, K, T, r)
    
