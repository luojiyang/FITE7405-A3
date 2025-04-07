import numpy as np
from scipy.stats import norm

class GeometricAsianPricer:
    def __init__(self, S=100.0, K=100.0, T=1.0, sigma=0.2, r=0.05, n=100, option_type='call'):
        """
        几何亚式期权定价模型
        
        参数:
            S (float): 标的资产现价 (默认: 100.0)
            K (float): 行权价 (默认: 100.0)
            T (float): 到期时间(年) (默认: 1.0)
            sigma (float): 波动率 (默认: 0.2)
            r (float): 无风险利率 (默认: 0.05)
            n (int): 观察次数 (默认: 100)
            option_type (str): 期权类型 ('call'或'put') (默认: 'call')
        """
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.sigma = float(sigma)
        self.r = float(r)
        self.n = int(n)
        self.option_type = option_type.lower()
        
        self._validate_parameters()
    
    def _validate_parameters(self):
        """参数验证"""
        if not all(x > 0 for x in [self.S, self.K, self.T, self.sigma, self.r]):
            raise ValueError("S, K, T, sigma, r 必须大于0")
        if self.n <= 0:
            raise ValueError("观察次数n必须大于0")
        if self.option_type not in ['call', 'put']:
            raise ValueError("option_type必须是'call'或'put'")
    
    def _calculate_parameters(self):
        """计算中间参数"""
        self.sigma_hat = self.sigma * np.sqrt((self.n + 1) * (2 * self.n + 1) / (6 * self.n**2))
        self.miu_hat = (self.r - 0.5 * self.sigma**2) * (self.n + 1) / (2 * self.n) + 0.5 * self.sigma_hat**2
        self.d1_hat = (np.log(self.S / self.K) + (self.miu_hat + 0.5 * self.sigma_hat**2) * self.T) / (
            self.sigma_hat * np.sqrt(self.T)
        )
        self.d2_hat = self.d1_hat - self.sigma_hat * np.sqrt(self.T)
    
    def _call_price(self):
        """计算看涨期权价格"""
        return np.exp(-self.r * self.T) * (
            self.S * np.exp(self.miu_hat * self.T) * norm.cdf(self.d1_hat) - 
            self.K * norm.cdf(self.d2_hat)
        )
    
    def _put_price(self):
        """计算看跌期权价格"""
        return np.exp(-self.r * self.T) * (
            self.K * norm.cdf(-self.d2_hat) - 
            self.S * np.exp(self.miu_hat * self.T) * norm.cdf(-self.d1_hat)
        )
    
    def calculate_price(self):
        """
        计算期权价格
        
        返回:
            dict: {
                'price': float,  # 期权价格
                'parameters': dict,  # 计算参数
                'status': str,  # 'success'/'error'
                'message': str  # 错误信息(如有)
            }
        """
        try:
            self._calculate_parameters()
            
            if self.option_type == 'call':
                price = self._call_price()
            else:  # put
                price = self._put_price()
            
            return {
                'price': price,
                'parameters': {
                    'S': self.S,
                    'K': self.K,
                    'T': self.T,
                    'sigma': self.sigma,
                    'r': self.r,
                    'n': self.n,
                    'option_type': self.option_type,
                    'sigma_hat': self.sigma_hat,
                    'miu_hat': self.miu_hat,
                    'd1_hat': self.d1_hat,
                    'd2_hat': self.d2_hat
                },
                'status': 'success',
                'message': None
            }
            
        except Exception as e:
            return {
                'price': None,
                'parameters': None,
                'status': 'error',
                'message': f"计算失败: {str(e)}"
            }