import numpy as np
from scipy.stats import norm

class ArithmeticAsianPricer:
    def __init__(self, S0=100, sigma=0.3, r=0.05, T=3.0, K=100, n=50, 
                 option_type='call', m=100000, control_variate='none'):
        """
        Asian Option Pricer for arithmetic and geometric Asian options
        
        Parameters:
            S0: Initial asset price (default 100)
            sigma: Volatility (default 0.3)
            r: Risk-free rate (default 0.05)
            T: Time to maturity in years (default 3.0)
            K: Strike price (default 100)
            n: Number of observation points (default 50)
            option_type: 'call' or 'put' (default 'call')
            m: Number of Monte Carlo paths (default 100,000)
            control_variate: 'none' or 'geometric' (default 'none')
        """
        self.S0 = S0
        self.sigma = sigma
        self.r = r
        self.T = T
        self.K = K
        self.n = n
        self.option_type = option_type.lower()
        self.m = m
        self.control_variate = control_variate
        self.dt = T / n
        
        # Validate parameters
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate input parameters"""
        if self.S0 <= 0:
            raise ValueError("Initial price S0 must be positive")
        if self.sigma <= 0:
            raise ValueError("Volatility sigma must be positive")
        if self.T <= 0:
            raise ValueError("Time to maturity T must be positive")
        if self.K <= 0:
            raise ValueError("Strike price K must be positive")
        if self.n <= 0:
            raise ValueError("Number of observations n must be positive")
        if self.m <= 0:
            raise ValueError("Number of paths m must be positive")
        if self.option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")
        if self.control_variate not in ['None', 'Geometric Asian']:
            raise ValueError("control_variate must be 'None' or 'Geometric Asian'")

    def _geometric_price(self):
        """Calculate closed-form solution for geometric Asian option"""
        Bg0 = self.S0
        sigma_g = self.sigma * np.sqrt((self.n + 1) * (2 * self.n + 1) / (6 * self.n ** 2))
        mu_g = self.r - 0.5 * self.sigma ** 2 + 0.5 * sigma_g ** 2
        d1 = (np.log(Bg0 / self.K) + (mu_g + 0.5 * sigma_g ** 2) * self.T) / (sigma_g * np.sqrt(self.T))
        d2 = d1 - sigma_g * np.sqrt(self.T)

        if self.option_type == 'call':
            price = np.exp(-self.r * self.T) * (Bg0 * np.exp(mu_g * self.T) * norm.cdf(d1) - 
                                               self.K * norm.cdf(d2))
        else:
            price = np.exp(-self.r * self.T) * (self.K * norm.cdf(-d2) - 
                                               Bg0 * np.exp(mu_g * self.T) * norm.cdf(-d1))
        return price

    def _generate_paths(self):
        """Generate asset price paths using Monte Carlo simulation"""
        np.random.seed(0)
        z = np.random.standard_normal((self.m, self.n))
        S = np.zeros((self.m, self.n + 1))
        S[:, 0] = self.S0

        for i in range(self.n):
            S[:, i + 1] = S[:, i] * np.exp((self.r - 0.5 * self.sigma ** 2) * self.dt + 
                                         self.sigma * np.sqrt(self.dt) * z[:, i])
        return S

    def calculate_price(self):
        """Calculate Asian option price with confidence interval"""
        try:
            # Generate paths
            S = self._generate_paths()
            
            # Calculate arithmetic average and payoff
            arithmetic_avg = np.mean(S[:, 1:], axis=1)
            payoff = (np.maximum(arithmetic_avg - self.K, 0) if self.option_type == 'call' 
                     else np.maximum(self.K - arithmetic_avg, 0))
            
            # Base Monte Carlo price
            price = np.exp(-self.r * self.T) * np.mean(payoff)
            std = np.std(payoff)
            conf_lower = price - 1.96 * std / np.sqrt(self.m)
            conf_upper = price + 1.96 * std / np.sqrt(self.m)

            # Control variate adjustment if specified
            if self.control_variate == 'Geometric Asian':
                geo_price = self._geometric_price()
                geometric_avg = np.exp(np.mean(np.log(S[:, 1:]), axis=1))
                geo_payoff = (np.maximum(geometric_avg - self.K, 0) if self.option_type == 'call' 
                             else np.maximum(self.K - geometric_avg, 0))
                
                cov = np.cov(payoff, geo_payoff)
                beta = cov[0, 1] / cov[1, 1]
                adjusted_payoff = payoff - beta * (geo_payoff - geo_price)
                
                price = np.exp(-self.r * self.T) * np.mean(adjusted_payoff)
                std = np.std(adjusted_payoff)
                conf_lower = price - 1.96 * std / np.sqrt(self.m)
                conf_upper = price + 1.96 * std / np.sqrt(self.m)

            return {
                'price': price,
                'conf_interval': (conf_lower, conf_upper),
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
