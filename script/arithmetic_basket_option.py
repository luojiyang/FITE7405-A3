import numpy as np


def arithmetic_basket_option_mc(S0_1, S0_2, K, sigma_1, sigma_2, rho, T, r, m):
    """
    蒙特卡洛模拟计算 算术篮子期权价格

    参数:
    S0_1 (float): 资产1的当前价格
    S0_2 (float): 资产2的当前价格
    K (float): 期权执行价格
    sigma_1 (float): 资产1的波动率
    sigma_2 (float): 资产2的波动率
    rho (float): 资产1和资产2的相关系数
    T (float): 期权到期时间
    r (float): 无风险利率
    m (int): 蒙特卡洛模拟的路径数量

    返回:
    float: 算术篮子期权的价格
    """
    # 设置随机数种子以保证结果可复现
    np.random.seed(0)
    dt = 0.01
    N = int(T / dt)
    # 构建协方差矩阵
    cov_matrix = [[sigma_1 ** 2, rho * sigma_1 * sigma_2], [rho * sigma_1 * sigma_2, sigma_2 ** 2]]
    # 生成相关的标准正态分布随机数
    z = np.random.multivariate_normal([0, 0], cov_matrix, (m, N))

    S1 = np.zeros((m, N + 1))
    S2 = np.zeros((m, N + 1))
    S1[:, 0] = S0_1
    S2[:, 0] = S0_2

    # 模拟资产1和资产2的价格路径
    for i in range(N):
        S1[:, i + 1] = S1[:, i] * np.exp((r - 0.5 * sigma_1 ** 2) * dt + np.sqrt(dt) * z[:, i, 0])
        S2[:, i + 1] = S2[:, i] * np.exp((r - 0.5 * sigma_2 ** 2) * dt + np.sqrt(dt) * z[:, i, 1])

    # 计算每条路径上资产1和资产2价格的算术平均值
    average_S1 = np.mean(S1, axis=1)
    average_S2 = np.mean(S2, axis=1)
    # 计算每条路径上的篮子期权收益
    basket_payoff = np.maximum(0.5 * average_S1 + 0.5 * average_S2 - K, 0)
    # 对篮子期权收益进行贴现得到期权价格
    option_price = np.exp(-r * T) * np.mean(basket_payoff)

    return option_price
