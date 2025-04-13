import numpy as np
from scipy.stats import norm


class BlackScholesPricer:
    def __init__(self, S=100.0, K=100.0, T=1.0, sigma=0.2, r=0.05, q=0.0, option_type='call'):
        """
        Black-Scholes期权定价计算器
        
        参数:
            S (float): 标的资产现价 (默认: 100.0)
            K (float): 行权价 (默认: 100.0)
            T (float): 到期时间(年) (默认: 1.0)
            sigma (float): 波动率 (默认: 0.2)
            r (float): 无风险利率 (默认: 0.05)
            q (float): 连续股息率/回购率 (默认: 0.0)
            option_type (str): 期权类型 ('call'或'put') (默认: 'call')
        """
        self.S = S
        self.K = K
        self.T = T
        self.sigma = sigma
        self.r = r
        self.q = q
        self.option_type = option_type
        
        # 参数验证
        self._validate_parameters()
        
        # 预计算中间变量
        self.d1, self.d2 = self.calculate_d1_d2()
        
    def _validate_parameters(self):
        """验证输入参数合理性"""
        if self.S <= 0:
            raise ValueError("标的资产价格S必须大于0")
        if self.K <= 0:
            raise ValueError("行权价K必须大于0")
        if self.T <= 0:
            raise ValueError("到期时间T必须大于0")
        if self.sigma <= 0:
            raise ValueError("波动率sigma必须大于0")
        if self.option_type.lower() not in ['call', 'put']:
            raise ValueError("option_type必须是'call'或'put'")
        
        self.option_type = self.option_type.lower()
        
    def calculate_d1_d2(self):
        """
        Calculate d1 and d2 parameters for Black-Scholes model with repo rate
        
        Parameters:
        S (float): spot price of the asset
        K (float): strike price
        T (float): time to maturity (in years)
        sigma (float): volatility
        r (float): risk-free interest rate
        q (float): repo rate (dividend yield for stocks)
        """
        d1 = (np.log(self.S / self.K) + ((self.r - self.q) * self.T)) / (self.sigma * np.sqrt(self.T)) + 0.5 * self.sigma * np.sqrt(self.T)
        d2 = (np.log(self.S / self.K) + ((self.r - self.q) * self.T)) / (self.sigma * np.sqrt(self.T)) - 0.5 * self.sigma * np.sqrt(self.T)
        return d1, d2
    
    def call_value(self,d1,d2):
        """Calculate call option value using Black-Scholes formula with repo rate"""
        return self.S * np.exp(-self.q * self.T) * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
    
    def put_value(self,d1,d2):
        """Calculate put option value using Black-Scholes formula with repo rate"""
        return self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * np.exp(-self.q * self.T) * norm.cdf(-d1)
    
    def calculate_option_price(self):
        """
        Calculate European option price using Black-Scholes model with repo rate
        
        Parameters:
        S (float): spot price of the asset
        K (float): strike price
        T (float): time to maturity (in years)
        sigma (float): volatility
        r (float): risk-free interest rate
        q (float): repo rate (dividend yield for stocks)
        option_type (str): 'call' or 'put'
        
        Returns:
        float: option price
        """
        try:
            # 计算d1/d2参数
            d1, d2 = self.calculate_d1_d2()
            
            # 计算期权价格
            if self.option_type.lower() == "call":
                price = self.call_value(d1, d2)
            elif self.option_type.lower() == "put":
                price = self.put_value(d1, d2)
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'.")

            return {
                'price': price,
                'status': 'success',
            }
            
        except Exception as e:
            return {
                'price': None,
                'status': 'error',
                'message': f"计算失败: {str(e)}"
            }