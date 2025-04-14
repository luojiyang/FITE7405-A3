import numpy as np
from scipy.stats import norm

class GeometricAsianPricer:
    def __init__(self, S=100.0, K=100.0, T=1.0, sigma=0.2, r=0.05, n=100, option_type='call'):
        """
        Pricing Model for Geometric Asian Options
        
        Parameters:
            S (float): Asset spot price (default: 100.0)
            K (float): Strike price (default: 100.0)
            T (float): Time to maturity(year) (default: 1.0)
            sigma (float): Volatitliy (default: 0.2)
            r (float): Risk-free interest rate (default: 0.05)
            n (int): Number of observation (default: 100)
            option_type (str): Option type ('call'或'put') (default: 'call')
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
        """Parameters valiation"""
        if not all(x > 0 for x in [self.S, self.K, self.T, self.sigma, self.r]):
            raise ValueError("S, K, T, sigma, r should be larger than 0")
        if self.n <= 0:
            raise ValueError("Times of obervation n should be larger than0")
        if self.option_type not in ['call', 'put']:
            raise ValueError("option_type must be'call' or 'put'")
    
    def _calculate_parameters(self):
        """Calculate the intermediate values"""
        self.sigma_hat = self.sigma * np.sqrt((self.n + 1) * (2 * self.n + 1) / (6 * self.n**2))
        self.miu_hat = (self.r - 0.5 * self.sigma**2) * (self.n + 1) / (2 * self.n) + 0.5 * self.sigma_hat**2
        self.d1_hat = (np.log(self.S / self.K) + (self.miu_hat + 0.5 * self.sigma_hat**2) * self.T) / (
            self.sigma_hat * np.sqrt(self.T)
        )
        self.d2_hat = self.d1_hat - self.sigma_hat * np.sqrt(self.T)
    
    def _call_price(self):
        """Calculate the call option price"""
        return np.exp(-self.r * self.T) * (
            self.S * np.exp(self.miu_hat * self.T) * norm.cdf(self.d1_hat) - 
            self.K * norm.cdf(self.d2_hat)
        )
    
    def _put_price(self):
        """Calculate the put option price"""
        return np.exp(-self.r * self.T) * (
            self.K * norm.cdf(-self.d2_hat) - 
            self.S * np.exp(self.miu_hat * self.T) * norm.cdf(-self.d1_hat)
        )
    
    def calculate_price(self):
        """
        Calculate the option price
        
        Return:
            dict: {
                'price': float,  # option price
                'parameters': dict,  # parameters
                'status': str,  # 'success'/'error'
                'message': str  # error message(if any)
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
                'message': f"Failed to calculate: {str(e)}"
            }