import numpy as np
from scipy.stats import norm


# F(sigma) function
def f_sigma(sigma,S, K, r, T, t, V, repo, option_type):
    d1 = (np.log(S / K) + (r - repo) * (T - t)) / (sigma * np.sqrt(T - t)) + 0.5 * sigma * np.sqrt(T - t)
    d2 = (np.log(S / K) + (r - repo) * (T - t)) / (sigma * np.sqrt(T - t)) - 0.5 * sigma * np.sqrt(T - t)
    if (option_type == 'cut'):
        return S * np.exp(-repo * (T - t)) * norm.cdf(d1) - K * np.exp(-r * (T - t)) * norm.cdf(d2) - V
    elif (option_type == 'put'):
        return K * np.exp(-r * (T - t)) * norm.cdf(-d2) - S * np.exp(-repo * (T - t)) * norm.cdf(-d1) - V
    return None

# F_prime_sigma function
def f_prime_sigma(sigma, S, K, r, T, t, repo):
    d1 = (np.log(S / K) + (r - repo) * (T - t)) / (sigma * np.sqrt(T - t)) + 0.5 * sigma * np.sqrt(T - t)
    return S * np.exp(-repo * (T - t)) * norm.pdf(d1) * np.sqrt(T - t)

# Newton method to find the implied volatility
def implied_volatility(S, K, r, T, t, repo, V, option_type):
    sigmahat = np.sqrt(2 * abs((np.log(S / K) + (r - repo) * (T - t)) / (T - t)))
    tol = 1e-8
    nmax = 100
    sigmadiff = 1
    n = 1
    sigma = sigmahat
    while sigmadiff > tol and n < nmax:
        sigma_delta = f_sigma(sigma, S, K, r, T, t, V ,repo, option_type) / f_prime_sigma(sigma, S, K, r, T, t, repo)
        sigma = sigma - sigma_delta
        sigmadiff = abs(sigma_delta)
        n = n + 1
    
    return sigma