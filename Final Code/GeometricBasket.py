import numpy as np
from scipy.stats import norm

class GeometricBasketPricer:
    def __init__(self, S_1=100, S_2=100, K=100, T=1.0, sigma_1=0.2, sigma_2=0.2, r=0.05, rho=0.5, optionType='call'):
        """
        Geometric Basket期权定价器
        
        参数:
            S_1: 资产1的现价 (默认100)
            S_2: 资产2的现价 (默认100)
            K: 行权价 (默认100)
            T: 到期时间(年) (默认1.0)
            sigma_1: 资产1的波动率 (默认0.2)
            sigma_2: 资产2的波动率 (默认0.2)
            r: 无风险利率 (默认0.05)
            rho: 相关系数 (默认0.5)
            optionType: 期权类型 'call' 或 'put' (默认'call')
        """
        self.S_1 = S_1
        self.S_2 = S_2
        self.K = K
        self.T = T
        self.sigma_1 = sigma_1
        self.sigma_2 = sigma_2
        self.r = r
        self.rho = rho
        self.optionType = optionType.lower()
        
        # 验证参数
        self._validate_parameters()
        
        # 计算中间变量
        self.B_g_0 = (self.S_1 * self.S_2) ** (1 / 2)
        self.sigma_B_g = (
            np.sqrt(2 * (self.sigma_1**2) + 2 * (self.sigma_2**2) + 2 * self.sigma_1 * self.sigma_2 * self.rho) / 2
        )
        self.miu_B_g = self.r - 0.5 * (self.sigma_1**2 + self.sigma_2**2) / 2 + 0.5 * self.sigma_B_g**2
        self.d1_hat = (np.log(self.B_g_0 / self.K) + (self.miu_B_g + 0.5 * self.sigma_B_g**2) * self.T) / (
            self.sigma_B_g * np.sqrt(self.T)
        )
        self.d2_hat = self.d1_hat - self.sigma_B_g * np.sqrt(self.T)

    def _validate_parameters(self):
        """验证输入参数是否合理"""
        if self.S_1 <= 0:
            raise ValueError("资产1现价S_1必须大于0")
        if self.S_2 <= 0:
            raise ValueError("资产2现价S_2必须大于0")
        if self.K <= 0:
            raise ValueError("行权价K必须大于0")
        if self.T <= 0:
            raise ValueError("到期时间T必须大于0")
        if self.sigma_1 <= 0:
            raise ValueError("资产1波动率sigma_1必须大于0")
        if self.sigma_2 <= 0:
            raise ValueError("资产2波动率sigma_2必须大于0")
        if self.rho < -1 or self.rho > 1:
            raise ValueError("相关系数rho必须在[-1, 1]之间")
        if self.optionType not in ['call', 'put']:
            raise ValueError("optionType必须是'call'或'put'")

    def _geo_basket_call(self):
        """计算几何篮子看涨期权价格"""
        return np.exp(-self.r * self.T) * (
            self.B_g_0 * np.exp(self.miu_B_g * self.T) * norm.cdf(self.d1_hat) - 
            self.K * norm.cdf(self.d2_hat)
        )

    def _geo_basket_put(self):
        """计算几何篮子看跌期权价格"""
        return np.exp(-self.r * self.T) * (
            self.K * norm.cdf(-self.d2_hat) - 
            self.B_g_0 * np.exp(self.miu_B_g * self.T) * norm.cdf(-self.d1_hat)
        )

    def calculate_price(self):
        """计算几何篮子期权价格"""
        try:
            if self.optionType == 'call':
                price = self._geo_basket_call()
            else:  # put
                price = self._geo_basket_put()

            # 封闭形式解没有置信区间
            conf_interval = (None, None)

            return {
                'price': price,
                'conf_interval': conf_interval,
                'status': 'success'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
