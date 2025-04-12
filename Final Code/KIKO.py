import numpy as np
from scipy.stats import norm
import sobol_seq

class KIKOPutPricer:
    def __init__(self, S0=100, sigma=0.2, r=0.05, T=1.0, K=100, L=80, U=120, n=50, R=10, num_paths=100000):
        """
        KIKO Put期权定价器
        
        参数:
            S0: 初始资产价格 (默认100)
            sigma: 波动率 (默认0.2)
            r: 无风险利率 (默认0.05)
            T: 到期时间(年) (默认1.0)
            K: 行权价 (默认100)
            L: 下敲入障碍 (默认80)
            U: 上敲出障碍 (默认120)
            n: 观察次数 (默认50)
            R: 敲出时的折扣金额 (默认10)
            num_paths: 模拟路径数 (默认100,000)
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
        self.dt = T / n
        
        # 验证参数
        self._validate_parameters()
    
    def _validate_parameters(self):
        """验证输入参数是否合理"""
        if self.L >= self.S0:
            raise ValueError("下敲入障碍L必须小于初始价格S0")
        if self.U <= self.S0:
            raise ValueError("上敲出障碍U必须大于初始价格S0")
        if self.T <= 0:
            raise ValueError("到期时间T必须大于0")
        if self.n <= 0:
            raise ValueError("观察次数n必须大于0")
    
    def generate_sobol_paths(self):
        """使用Sobol序列生成资产价格路径"""
        max_dim = 40
        num_blocks = (self.n + max_dim - 1) // max_dim
        
        Z = np.zeros((self.num_paths, self.n))
        for block in range(num_blocks):
            start = block * max_dim
            end = min((block + 1) * max_dim, self.n)
            dim = end - start
            sobol = sobol_seq.i4_sobol_generate(dim, self.num_paths)
            Z[:, start:end] = norm.ppf(sobol)
        
        paths = np.zeros((self.num_paths, self.n + 1))
        paths[:, 0] = self.S0
        
        drift = (self.r - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * np.sqrt(self.dt)
        
        log_returns = drift + diffusion * Z
        cum_log_returns = np.cumsum(log_returns, axis=1)
        paths[:, 1:] = self.S0 * np.exp(cum_log_returns)
        
        return paths
    
    def calculate_price(self):
        """计算KIKO Put期权价格和Delta"""
        try:
            # 计算价格
            paths = self.generate_sobol_paths()
            payoff = np.zeros(self.num_paths)
            
            knock_out_mask = np.any(paths >= self.U, axis=1)
            knock_in_mask = np.any(paths <= self.L, axis=1)
            
            if np.any(knock_out_mask):
                knock_out_idx = np.argmax(paths >= self.U, axis=1)
                knock_out_times = knock_out_idx * self.dt
                payoff[knock_out_mask] = self.R * np.exp(-self.r * knock_out_times[knock_out_mask])
            
            in_not_out = knock_in_mask & ~knock_out_mask
            payoff[in_not_out] = np.maximum(self.K - paths[in_not_out, -1], 0) * np.exp(-self.r * self.T)
            
            price = np.mean(payoff)
            std = np.std(payoff)
            conf_lower = price - 1.96 * std / np.sqrt(self.num_paths)
            conf_upper = price + 1.96 * std / np.sqrt(self.num_paths)
            
            # 计算Delta
            original_S0 = self.S0
            dS = original_S0 * 0.01  # 1% of S0
            
            self.S0 = original_S0 + dS
            price_up = np.mean(self._calculate_payoff())
            
            self.S0 = original_S0 - dS
            price_down = np.mean(self._calculate_payoff())
            
            self.S0 = original_S0
            delta = (price_up - price_down) / (2 * dS)
            
            return {
                'price': price,
                'conf_interval': (conf_lower, conf_upper),
                'delta': delta,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _calculate_payoff(self):
        """辅助方法，用于Delta计算中的价格计算"""
        paths = self.generate_sobol_paths()
        payoff = np.zeros(self.num_paths)
        
        knock_out_mask = np.any(paths >= self.U, axis=1)
        knock_in_mask = np.any(paths <= self.L, axis=1)
        
        if np.any(knock_out_mask):
            knock_out_idx = np.argmax(paths >= self.U, axis=1)
            knock_out_times = knock_out_idx * self.dt
            payoff[knock_out_mask] = self.R * np.exp(-self.r * knock_out_times[knock_out_mask])
        
        in_not_out = knock_in_mask & ~knock_out_mask
        payoff[in_not_out] = np.maximum(self.K - paths[in_not_out, -1], 0) * np.exp(-self.r * self.T)
        
        return payoff