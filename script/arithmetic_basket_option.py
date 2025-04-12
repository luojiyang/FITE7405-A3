# S0_1 资产1的当前价格（即期价格）	几何篮子期权的 S₁(0)
# S0_2 资产2的当前价格（即期价格）	几何篮子期权的 S₂(0)
# sigma_1  资产1的波动率（年化）	几何篮子期权的 σ₁
# sigma_2 资产2的波动率（年化）	几何篮子期权的 σ₂
# rho	资产1和资产2的相关系数（范围：[-1, 1]）	几何篮子期权的 ρ
# r	无风险利率（年化，连续复利）	几何篮子期权的 r
# T	期权到期时间（年）	几何篮子期权的 T
# K	期权的执行价格	几何篮子期权的 K
# option_type	str	期权类型，'call' 或 'put'	作业要求的 option type
# m	蒙特卡洛模拟的路径数量	作业要求的 number of paths

# control_variate	str	控制变量方法，可选：
# - 'none'：不使用控制变量
# - 'geometric'：使用几何篮子期权作为控制变量	作业要求的 control variate method


import numpy as np
from scipy.stats import norm


def geometric_basket_option(S0_1, S0_2, sigma_1, sigma_2, rho, r, T, K, option_type):
    """计算几何篮子期权的闭式解"""
    Bg0 = np.sqrt(S0_1 * S0_2)
    sigma_bg = np.sqrt(sigma_1 ** 2 + sigma_2 ** 2 + 2 * rho * sigma_1 * sigma_2) / 2
    mu_bg = r - 0.5 * (sigma_1 ** 2 + sigma_2 ** 2) / 2 + 0.5 * sigma_bg ** 2
    d1 = (np.log(Bg0 / K) + (mu_bg + 0.5 * sigma_bg ** 2) * T) / (sigma_bg * np.sqrt(T))
    d2 = d1 - sigma_bg * np.sqrt(T)

    if option_type == 'call':
        price = np.exp(-r * T) * (Bg0 * np.exp(mu_bg * T) * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        price = np.exp(-r * T) * (K * norm.cdf(-d2) - Bg0 * np.exp(mu_bg * T) * norm.cdf(-d1))
    return price


def arithmetic_basket_option_mc(S0_1, S0_2, sigma_1, sigma_2, rho, r, T, K, option_type, m, control_variate='none'):
    """蒙特卡洛模拟计算算术篮子期权价格及置信区间（支持控制变量）"""
    np.random.seed(0)
    cov_matrix = [[1, rho], [rho, 1]]
    z = np.random.multivariate_normal([0, 0], cov_matrix, m)

    # 生成到期价格
    S1_T = S0_1 * np.exp((r - 0.5 * sigma_1 ** 2) * T + sigma_1 * np.sqrt(T) * z[:, 0])
    S2_T = S0_2 * np.exp((r - 0.5 * sigma_2 ** 2) * T + sigma_2 * np.sqrt(T) * z[:, 1])
    B_a = (S1_T + S2_T) / 2
    payoff = np.maximum(B_a - K, 0) if option_type == 'call' else np.maximum(K - B_a, 0)
    mc_price = np.exp(-r * T) * np.mean(payoff)
    std_err = 1.96 * np.std(payoff) / np.sqrt(m)
    conf_interval = (mc_price - std_err, mc_price + std_err)

    # 控制变量修正
    if control_variate == 'geometric':
        geo_price = geometric_basket_option(S0_1, S0_2, sigma_1, sigma_2, rho, r, T, K, option_type)
        B_g = np.sqrt(S1_T * S2_T)
        geo_payoff = np.maximum(B_g - K, 0) if option_type == 'call' else np.maximum(K - B_g, 0)
        cov = np.cov(payoff, geo_payoff)
        beta = cov[0, 1] / cov[1, 1]
        adjusted_payoff = payoff - beta * (geo_payoff - geo_price)
        mc_price_cv = np.exp(-r * T) * np.mean(adjusted_payoff)
        std_err_cv = 1.96 * np.std(adjusted_payoff) / np.sqrt(m)
        return mc_price_cv, (mc_price_cv - std_err_cv, mc_price_cv + std_err_cv)

    return mc_price, conf_interval

# 调用示例 篮子期权测试
# price, (low, high) = arithmetic_basket_option_mc(
#     S0_1=100, S0_2=100, sigma_1=0.3, sigma_2=0.3, rho=0.5,
#     r=0.05, T=3, K=100, option_type='Put', m=100000, control_variate='geometric'
# )