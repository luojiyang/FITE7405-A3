import numpy as np
from scipy.stats import norm

class GeometricBasketPricer:
    def __init__(self, S_1=100, S_2=100, K=100, T=1.0, sigma_1=0.2, sigma_2=0.2, r=0.05, rho=0.5, optionType='call'):
        """
        Pricing model for Geometric Basket options
        
        Parameters:
            S_1: Spot price of asset 1 (default: 100)
            S_2: Spot price of asset 2 (default: 100)
            K: Strike (default: 100)
            T: Time to maturity(year) (default: 1.0)
            sigma_1: Volatility of asset 1 (default: 0.2)
            sigma_2: Volatility of asset 2 (default: 0.2)
            r: Risk-free interest rate (default: 0.05)
            rho: Repo rate (default: 0.5)
            optionType: Option type:'call' or 'put' (default: 'call')
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
        
        # Validate the parameters
        self._validate_parameters()
        
        # Calculate the intermediate values
        self.B_g_0 = (self.S_1 * self.S_2) ** (1 / 2)
        self.sigma_B_g = (
            np.sqrt((self.sigma_1**2) + (self.sigma_2**2) + 2 * self.sigma_1 * self.sigma_2 * self.rho) / 2
        )
        self.miu_B_g = self.r - 0.5 * (self.sigma_1**2 + self.sigma_2**2) / 2 + 0.5 * self.sigma_B_g**2
        self.d1_hat = (np.log(self.B_g_0 / self.K) + (self.miu_B_g + 0.5 * self.sigma_B_g**2) * self.T) / (
            self.sigma_B_g * np.sqrt(self.T)
        )
        self.d2_hat = self.d1_hat - self.sigma_B_g * np.sqrt(self.T)

    def _validate_parameters(self):
        """Validate the input parameters"""
        if self.S_1 <= 0:
            raise ValueError("Spot price of asset 1 must be larger than 0")
        if self.S_2 <= 0:
            raise ValueError("Spot price of asset 2 must be larger than0")
        if self.K <= 0:
            raise ValueError("Strike K must be0")
        if self.T <= 0:
            raise ValueError("Time to maturity T must be larget than 0")
        if self.sigma_1 <= 0:
            raise ValueError("Volatility of asset 1 must be larger than 0")
        if self.sigma_2 <= 0:
            raise ValueError("Volatility of asset 2 must be larger than 0")
        if self.rho < -1 or self.rho > 1:
            raise ValueError("Repo rate rho should be within [-1, 1]")
        if self.optionType not in ['call', 'put']:
            raise ValueError("optionType should be 'call'or 'put'")

    def _geo_basket_call(self):
        """Calculate the price of geometric basket call option"""
        return np.exp(-self.r * self.T) * (
            self.B_g_0 * np.exp(self.miu_B_g * self.T) * norm.cdf(self.d1_hat) - 
            self.K * norm.cdf(self.d2_hat)
        )

    def _geo_basket_put(self):
        """Calculate the price of geometric basket put option"""
        return np.exp(-self.r * self.T) * (
            self.K * norm.cdf(-self.d2_hat) - 
            self.B_g_0 * np.exp(self.miu_B_g * self.T) * norm.cdf(-self.d1_hat)
        )

    def calculate_price(self):
        """Calculate the option price"""
        try:
            if self.optionType == 'call':
                price = self._geo_basket_call()
            else:  # put
                price = self._geo_basket_put()

            # No confidence interval for closed-form solution
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
