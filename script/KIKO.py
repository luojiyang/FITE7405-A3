import numpy as np
from scipy.stats import norm
import sobol_seq

class KIKOPutPricer:
    def __init__(self, S0, sigma, r, T, K, L, U, n, R, num_paths=100000):
        """
        初始化KIKO Put期权的参数
        S0: 初始资产价格
        sigma: 波动率
        r: 无风险利率
        T: 到期时间
        K: 行权价
        L: 下敲入障碍
        U: 上敲出障碍
        n: 观察次数
        R: 折扣金额
        num_paths: 模拟路径数
        """
        self.S0 = S0
        self.sigma = sigma
        self.r = r
        self.T = T
        self.K = K
        self.L = L
        self.U = U
        self.n = n
        self.R = R
        self.num_paths = num_paths
        self.dt = T / n  # 时间步长

    def generate_sobol_paths(self):
        max_dim = 40  # Sobol序列最大维度
        num_blocks = (self.n + max_dim - 1) // max_dim  # 计算需要的块数
        Z = np.zeros((self.num_paths, self.n))  # 初始化标准正态随机数矩阵
        
        for block in range(num_blocks):
            start = block * max_dim
            end = min((block + 1) * max_dim, self.n)
            dim = end - start
            sobol = sobol_seq.i4_sobol_generate(dim, self.num_paths)
            Z[:, start:end] = norm.ppf(sobol)
        
        # 初始化价格路径
        paths = np.zeros((self.num_paths, self.n + 1))
        paths[:, 0] = self.S0
        
        # 生成资产价格路径
        drift = (self.r - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * np.sqrt(self.dt)

        log_returns = drift + diffusion * Z
        cum_log_returns = np.cumsum(log_returns, axis=1)
        paths[:, 1:] = self.S0 * np.exp(cum_log_returns)
        return paths

    def price(self):
        """
        计算KIKO Put期权价格
        """
        paths = self.generate_sobol_paths()
        payoff = np.zeros(self.num_paths)
        
        for i in range(self.num_paths):
            path = paths[i, :]
            knocked_out = False
            knocked_in = False
            
            # 检查敲出和敲入条件
            for t in range(self.n + 1):
                # 上敲出检查
                if path[t] >= self.U:
                    payoff[i] = self.R * np.exp(-self.r * t * self.dt)
                    knocked_out = True
                    break
                # 下敲入检查
                if path[t] <= self.L:
                    knocked_in = True
            
            # 如果敲入但未敲出，计算到期时的看跌期权收益
            if knocked_in and not knocked_out:
                payoff[i] = max(self.K - path[-1], 0) * np.exp(-self.r * self.T)
        
        # 计算平均折现收益
        price = np.mean(payoff)
        std = np.std(payoff)
        conf_lower = price - 1.96 * std / np.sqrt(self.num_paths)
        conf_upper = price + 1.96 * std / np.sqrt(self.num_paths)
        return price, (conf_lower, conf_upper)

    def delta(self, dS=0.01):
        """
        计算KIKO Put的Delta（使用有限差分法）
        """
        # 当前价格
        base_price = self.price()[0]
        
        # 轻微上调S0后的价格
        self.S0 += dS
        up_price = self.price()[0] 
        
        # 恢复S0
        self.S0 -= dS
        
        # 计算Delta
        delta = (up_price - base_price) / dS
        return delta

# 测试代码
if __name__ == "__main__":
    # 使用文档中的默认参数
    pricer = KIKOPutPricer(
        S0=100,      # 初始价格
        sigma=0.3,   # 波动率
        r=0.05,      # 无风险利率
        T=3,         # 到期时间
        K=100,       # 行权价
        L=90,        # 下敲入障碍
        U=120,       # 上敲出障碍
        n=50,        # 观察次数
        R=5          # 折扣金额
    )
    
    price, conf_interval = pricer.price()  # 解包为 price 和 conf_interval
    delta = pricer.delta()

    print(f"KIKO Put Price: {price:.4f}")
    print(f"Confidence Interval: [{conf_interval[0]:.4f}, {conf_interval[1]:.4f}]")
    print(f"KIKO Put Delta: {delta:.4f}")