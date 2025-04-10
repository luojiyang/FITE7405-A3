import numpy as np
from scipy.stats import norm

class ImpliedVolatility:
  def __init__(self, S=100.0, K=100.0, T=1.0, r=0.05, q=0.0, option_premium=None, option_type='call'):
    """
    隐含波动率
    
    参数:
        S (float): 标的资产现价 (默认: 100.0)
        K (float): 行权价 (默认: 100.0)
        T (float): 到期时间(年) (默认: 1.0)
        r (float): 无风险利率 (默认: 0.05)
        q (float): 连续股息率/回购率 (默认: 0.0)
        option_type (str): 期权类型 ('call'或'put') (默认: 'call')
        option_premium (float): 期权市场价格/权利金 (默认: None)
    """
    self.S = S
    self.K = K
    self.T = T
    self.r = r
    self.q = q
    self.option_type = option_type.lower()
    self.option_premium = option_premium if option_premium is not None else None
    
    self._validate_parameters()
  
  def _validate_parameters(self):
    """参数验证"""
    if not all(x > 0 for x in [self.S, self.K, self.T]):
        raise ValueError("S, K, T必须大于0")
    if self.option_type not in ['call', 'put']:
        raise ValueError("option_type必须是'call'或'put'")
    if self.option_premium is not None and self.option_premium <= 0:
        raise ValueError("option_premium必须大于0")
  
  def _calculate_d1_d2(self, sigma):
    """计算d1和d2参数（用于隐含波动率计算）"""
    d1 = (np.log(self.S/self.K) + (self.r - self.q + 0.5*sigma**2)*self.T) 
    d1 /= (sigma * np.sqrt(self.T))
    d2 = d1 - sigma * np.sqrt(self.T)
    return d1, d2
  
  def calculate_price(self, sigma=None):
    """
    计算期权价格
    
    参数:
        sigma (float): 指定波动率（默认使用初始化参数）
        
    返回:
        float: 期权理论价格
    """
    sigma = sigma if sigma is not None else getattr(self, 'sigma', 0.2)  # 默认波动率0.2
    d1, d2 = self._calculate_d1_d2(sigma)
    
    if self.option_type == 'call':
        return self.S * np.exp(-self.q*self.T) * norm.cdf(d1) - \
                self.K * np.exp(-self.r*self.T) * norm.cdf(d2)
    else:
        return self.K * np.exp(-self.r*self.T) * norm.cdf(-d2) - \
                self.S * np.exp(-self.q*self.T) * norm.cdf(-d1)
  
  def calculate_implied_vol(self, max_iter=100000, tol=1e-6):
    """
    计算隐含波动率（牛顿法）
    
    参数:
        max_iter (int): 最大迭代次数 (默认: 100)
        tol (float): 收敛容差 (默认: 1e-6)
        
    返回:
        dict: {
            'implied_vol': float,  # 隐含波动率
            'iterations': int,     # 实际迭代次数
            'status': str          # 'converged'/'max_iter_reached'/'error'
            'message': str         # 错误信息（如有）
        }
    """
    if self.option_premium is None:
        return {
            'status': 'error',
            'message': '未设置option_premium（期权市场价格）'
        }
    
    try:
        # 初始猜测（Manaster & Koehler方法）
        sigma = np.sqrt(2*np.abs((np.log(self.S/self.K) + (self.r-self.q)*self.T)/self.T))
        
        for i in range(max_iter):
            d1, d2 = self._calculate_d1_d2(sigma)
            
            # 计算理论价格和vega
            if self.option_type == 'call':
                price = self.S * np.exp(-self.q*self.T) * norm.cdf(d1) - \
                        self.K * np.exp(-self.r*self.T) * norm.cdf(d2)
                vega = self.S * np.exp(-self.q*self.T) * norm.pdf(d1) * np.sqrt(self.T)
            else:
                price = self.K * np.exp(-self.r*self.T) * norm.cdf(-d2) - \
                        self.S * np.exp(-self.q*self.T) * norm.cdf(-d1)
                vega = self.S * np.exp(-self.q*self.T) * norm.pdf(d1) * np.sqrt(self.T)
            
            # 检查收敛
            diff = price - self.option_premium
            if abs(diff) < tol:
                return {
                    'implied_vol': sigma,
                    'iterations': i+1,
                    'status': 'converged'
                }
            
            # 牛顿法迭代（防止除零）
            if vega < 1e-12:
                break
            sigma -= diff / vega
        
        return {
            'implied_vol': sigma,
            'iterations': max_iter,
            'status': 'max_iter_reached',
            'message': f'达到最大迭代次数{max_iter}（未收敛）'
        }
        
    except Exception as e:
        return {
            'implied_vol': None,
            'iterations': 0,
            'status': 'error',
            'message': f'计算失败: {str(e)}'
        }