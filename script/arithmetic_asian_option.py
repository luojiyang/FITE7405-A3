import numpy as np

def arithmetic_asian_option_mc(S0, K, T, sigma, r, m):
    """
    蒙特卡洛模拟计算 算术亚式期权的价格和95%置信区间。

    参数:
    S0 (float): 当前标的资产价格
    K (float): 期权执行价格
    T (float): 期权到期时间
    sigma (float): 标的资产的波动率
    r (float): 无风险利率
    m (int): 蒙特卡洛模拟的路径数量

    返回:
    tuple: 包含期权价格和95%置信区间的元组
    """
    # 设置随机数种子以保证结果可复现
    np.random.seed(0)
    dt = 0.01
    N = int(T / dt)
    # 生成标准正态分布的随机数矩阵，形状为(m, N)
    z = np.random.standard_normal((m, N))
    S = np.zeros((m, N + 1))
    S[:, 0] = S0

    # 模拟资产价格路径
    for i in range(N):
        S[:, i + 1] = S[:, i] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z[:, i])

    # 计算每条路径上资产价格的算术平均值
    average_S = np.mean(S, axis=1)
    # 计算每条路径上的期权收益
    payoff = np.maximum(average_S - K, 0)
    # 对期权收益进行贴现得到期权价格
    option_price = np.exp(-r * T) * np.mean(payoff)

    # 计算收益的标准差
    std_dev = np.std(payoff)
    # 计算95%置信区间的宽度
    conf_interval = 1.96 * std_dev / np.sqrt(m)

    return option_price, (option_price - conf_interval, option_price + conf_interval)
