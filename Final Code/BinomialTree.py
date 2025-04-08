import numpy as np

class BinomialTreePricer:
    def __init__(self, S=100, K=100, T=1.0, sigma=0.2, r=0.05, n=100, optionType='call'):
        """
        Binomial Tree期权定价器
        
        参数:
            S: 当前股票价格 (默认100)
            K: 行权价 (默认100)
            T: 到期时间(年) (默认1.0)
            sigma: 波动率 (默认0.2)
            r: 无风险利率 (默认0.05)
            n: 步数 (默认100)
            optionType: 期权类型 'call' 或 'put' (默认'call')
        """
        self.S = S
        self.K = K
        self.T = T
        self.sigma = sigma
        self.r = r
        self.n = n
        self.optionType = optionType.lower()
        
        # 验证参数
        self._validate_parameters()
        
        # 计算常用变量
        self.delta_t = T / n
        self.u = np.exp(sigma * np.sqrt(self.delta_t))
        self.d = 1 / self.u
        self.p = (np.exp(r * self.delta_t) - self.d) / (self.u - self.d)
        self.df = np.exp(-r * self.delta_t)

    def _validate_parameters(self):
        """验证输入参数是否合理"""
        if self.S <= 0:
            raise ValueError("当前股票价格S必须大于0")
        if self.K <= 0:
            raise ValueError("行权价K必须大于0")
        if self.T <= 0:
            raise ValueError("到期时间T必须大于0")
        if self.sigma <= 0:
            raise ValueError("波动率sigma必须大于0")
        if self.n <= 0:
            raise ValueError("步数n必须大于0")
        if self.optionType not in ['call', 'put']:
            raise ValueError("optionType必须是'call'或'put'")

    def calculate_price(self):
        """计算期权价格"""
        try:
            # 计算到期时的资产价格
            prices = np.zeros(self.n + 1)
            for i in range(self.n + 1):
                prices[i] = self.S * (self.u ** (self.n - i)) * (self.d ** i)

            # 计算到期时的期权价值
            values = np.zeros(self.n + 1)
            if self.optionType == 'call':
                for i in range(self.n + 1):
                    values[i] = max(0, prices[i] - self.K)
            elif self.optionType == 'put':
                for i in range(self.n + 1):
                    values[i] = max(0, self.K - prices[i])

            # 向后归纳计算期权价格
            for step in range(self.n - 1, -1, -1):
                for i in range(step + 1):
                    prices[i] = prices[i] / self.u
                    if self.optionType == 'call':
                        values[i] = max(0, prices[i] - self.K, 
                                      self.df * (self.p * values[i] + (1 - self.p) * values[i + 1]))
                    elif self.optionType == 'put':
                        values[i] = max(0, self.K - prices[i], 
                                      self.df * (self.p * values[i] + (1 - self.p) * values[i + 1]))

            price = values[0]


            return {
                'price': price,
                'status': 'success'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
