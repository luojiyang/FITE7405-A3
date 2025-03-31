import numpy as np

def binomialTree(S, K, T, sigma, r, n, optionType):
    '''
    Optimized binomial tree implementation using dynamic programming.

    S: current stock price
    K: strike price
    T: maturity time
    sigma: volatility
    r: risk-free rate
    n: number of steps
    optionType: 'call' or 'put'
    '''
    delta_t = T / n
    u = np.exp(sigma * np.sqrt(delta_t))
    d = 1 / u
    p = (np.exp(r * delta_t) - d) / (u - d)
    df = np.exp(-r * delta_t)

    # Calculate asset prices at maturity
    prices = np.zeros(n + 1)
    for i in range(n + 1):
        prices[i] = S * (u ** (n - i)) * (d ** i)
    

    # Calculate option values at maturity
    values = np.zeros(n + 1)
    if optionType == 'call':
        for i in range(n + 1):
            values[i] = max(0, prices[i] - K)
    elif optionType == 'put':
        for i in range(n + 1):
            values[i] = max(0, K - prices[i])
    
    # Backward induction to calculate option price at the root
    for step in range(n - 1, -1, -1):
        for i in range(step + 1):
            # update the price on the current step by discounting
            prices[i] = prices[i] / u
            if optionType == 'call':
                values[i] = max(0,prices[i] - K, df * (p * values[i] + (1 - p) * values[i + 1]))
            elif optionType == 'put':
                values[i] = max(0,K - prices[i], df * (p * values[i] + (1 - p) * values[i + 1]))
            else:
                return "Invalid option"
    
    return values[0]

