import numpy as np
from scipy.stats import norm

# S0 标的资产的当前价格（即期价格）	几何亚式期权的 S(0)
# sigma	标的资产的波动率（年化）	几何亚式期权的 σ
# r	无风险利率（年化，连续复利）	几何亚式期权的 r
# T	期权到期时间（年）	几何亚式期权的 T
# K	期权的执行价格	几何亚式期权的 K
# n	观察次数（用于计算平均价格的观测点数）	几何亚式期权的 n
# option_type	str	期权类型，'call' 或 'put'	作业要求的 option type
# m	蒙特卡洛模拟的路径数量	作业要求的 number of paths

# control_variate	str	控制变量方法，可选：
# - 'none'：不使用控制变量
# - 'geometric'：使用几何亚式期权作为控制变量	作业要求的 control variate method

def geometric_asian_option(S0, sigma, r, T, K, n, option_type):
    """计算几何亚式期权的闭式解"""
    Bg0 = S0  # 初始几何平均为S0
    sigma_g = sigma * np.sqrt((n + 1) * (2 * n + 1) / (6 * n ** 2))
    mu_g = r - 0.5 * sigma ** 2 + 0.5 * sigma_g ** 2
    d1 = (np.log(Bg0 / K) + (mu_g + 0.5 * sigma_g ** 2) * T) / (sigma_g * np.sqrt(T))
    d2 = d1 - sigma_g * np.sqrt(T)

    if option_type == 'call':
        price = np.exp(-r * T) * (Bg0 * np.exp(mu_g * T) * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        price = np.exp(-r * T) * (K * norm.cdf(-d2) - Bg0 * np.exp(mu_g * T) * norm.cdf(-d1))
    return price


def arithmetic_asian_option_mc(S0, sigma, r, T, K, n, option_type, m, control_variate='none'):
    """蒙特卡洛模拟计算算术亚式期权价格及置信区间（支持控制变量）"""
    np.random.seed(0)
    dt = T / n
    z = np.random.standard_normal((m, n))
    S = np.zeros((m, n + 1))
    S[:, 0] = S0

    # 生成资产价格路径（在n个观察点）
    for i in range(n):
        S[:, i + 1] = S[:, i] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z[:, i])

    # 计算算术平均（排除初始价格S0）
    arithmetic_avg = np.mean(S[:, 1:], axis=1)
    payoff = np.maximum(arithmetic_avg - K, 0) if option_type == 'call' else np.maximum(K - arithmetic_avg, 0)
    mc_price = np.exp(-r * T) * np.mean(payoff)
    std_err = 1.96 * np.std(payoff) / np.sqrt(m)
    conf_interval = (mc_price - std_err, mc_price + std_err)

    # 控制变量修正
    if control_variate == 'geometric':
        geo_price = geometric_asian_option(S0, sigma, r, T, K, n, option_type)
        geometric_avg = np.exp(np.mean(np.log(S[:, 1:]), axis=1))
        geo_payoff = np.maximum(geometric_avg - K, 0) if option_type == 'call' else np.maximum(K - geometric_avg, 0)
        cov = np.cov(payoff, geo_payoff)
        beta = cov[0, 1] / cov[1, 1]
        adjusted_payoff = payoff - beta * (geo_payoff - geo_price)
        mc_price_cv = np.exp(-r * T) * np.mean(adjusted_payoff)
        std_err_cv = 1.96 * np.std(adjusted_payoff) / np.sqrt(m)
        return mc_price_cv, (mc_price_cv - std_err_cv, mc_price_cv + std_err_cv)

    return mc_price, conf_interval

# 调用示例
# price, (low, high) = arithmetic_asian_option_mc(
#     S0=100, sigma=0.3, r=0.05, T=3, K=100, n=50,
#     option_type='Put', m=100000, control_variate='geometric'
# )
