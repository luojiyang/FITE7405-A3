import numpy as np
from scipy.stats import norm

class ArithmeticBasketPricer:
    def __init__(self, S0_1=100, S0_2=100, sigma_1=0.3, sigma_2=0.3, rho=0.5, 
                 r=0.05, T=3.0, K=100, option_type='call', m=100000, control_variate='None'):
        """
        Basket Option Pricer for arithmetic and geometric basket options
        
        Parameters:
            S0_1: Initial price of asset 1 (default 100)
            S0_2: Initial price of asset 2 (default 100)
            sigma_1: Volatility of asset 1 (default 0.3)
            sigma_2: Volatility of asset 2 (default 0.3)
            rho: Correlation coefficient between assets (default 0.5)
            r: Risk-free rate (default 0.05)
            T: Time to maturity in years (default 3.0)
            K: Strike price (default 100)
            option_type: 'call' or 'put' (default 'call')
            m: Number of Monte Carlo paths (default 100,000)
            control_variate: 'none' or 'geometric' (default 'none')
        """
        self.S0_1 = S0_1
        self.S0_2 = S0_2
        self.sigma_1 = sigma_1
        self.sigma_2 = sigma_2
        self.rho = rho
        self.r = r
        self.T = T
        self.K = K
        self.option_type = option_type.lower()
        self.m = m
        self.control_variate = control_variate
        
        # Validate parameters
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate input parameters"""
        if self.S0_1 <= 0 or self.S0_2 <= 0:
            raise ValueError("Initial prices S0_1 and S0_2 must be positive")
        if self.sigma_1 <= 0 or self.sigma_2 <= 0:
            raise ValueError("Volatilities sigma_1 and sigma_2 must be positive")
        if self.rho < -1 or self.rho > 1:
            raise ValueError("Correlation coefficient rho must be between -1 and 1")
        if self.T <= 0:
            raise ValueError("Time to maturity T must be positive")
        if self.K <= 0:
            raise ValueError("Strike price K must be positive")
        if self.m <= 0:
            raise ValueError("Number of paths m must be positive")
        if self.option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")
        if self.control_variate not in ['None', 'Geometric Basket']:
            raise ValueError("control_variate must be 'None' or 'Geometric Basket'")

    def _geometric_price(self):
        """Calculate closed-form solution for geometric basket option"""
        Bg0 = np.sqrt(self.S0_1 * self.S0_2)
        sigma_bg = np.sqrt(self.sigma_1 ** 2 + self.sigma_2 ** 2 + 
                          2 * self.rho * self.sigma_1 * self.sigma_2) / 2
        mu_bg = self.r - 0.5 * (self.sigma_1 ** 2 + self.sigma_2 ** 2) / 2 + 0.5 * sigma_bg ** 2
        d1 = (np.log(Bg0 / self.K) + (mu_bg + 0.5 * sigma_bg ** 2) * self.T) / (sigma_bg * np.sqrt(self.T))
        d2 = d1 - sigma_bg * np.sqrt(self.T)

        if self.option_type == 'call':
            price = np.exp(-self.r * self.T) * (Bg0 * np.exp(mu_bg * self.T) * norm.cdf(d1) - 
                                               self.K * norm.cdf(d2))
        else:
            price = np.exp(-self.r * self.T) * (self.K * norm.cdf(-d2) - 
                                               Bg0 * np.exp(mu_bg * self.T) * norm.cdf(-d1))
        return price

    def _generate_paths(self):
        """Generate asset price paths at maturity using Monte Carlo simulation"""
        np.random.seed(0)
        cov_matrix = [[1, self.rho], [self.rho, 1]]
        z = np.random.multivariate_normal([0, 0], cov_matrix, self.m)

        S1_T = self.S0_1 * np.exp((self.r - 0.5 * self.sigma_1 ** 2) * self.T + 
                                self.sigma_1 * np.sqrt(self.T) * z[:, 0])
        S2_T = self.S0_2 * np.exp((self.r - 0.5 * self.sigma_2 ** 2) * self.T + 
                                self.sigma_2 * np.sqrt(self.T) * z[:, 1])
        return S1_T, S2_T

    def calculate_price(self):
        """Calculate basket option price with confidence interval"""
        try:
            # Generate paths
            S1_T, S2_T = self._generate_paths()
            
            # Calculate arithmetic average and payoff
            B_a = (S1_T + S2_T) / 2
            payoff = (np.maximum(B_a - self.K, 0) if self.option_type == 'call' 
                     else np.maximum(self.K - B_a, 0))
            
            # Base Monte Carlo price
            price = np.exp(-self.r * self.T) * np.mean(payoff)
            std = np.std(payoff)
            conf_lower = price - 1.96 * std / np.sqrt(self.m)
            conf_upper = price + 1.96 * std / np.sqrt(self.m)

            # Control variate adjustment if specified
            if self.control_variate == 'Geometric Basket':
                geo_price = self._geometric_price()
                B_g = np.sqrt(S1_T * S2_T)
                geo_payoff = (np.maximum(B_g - self.K, 0) if self.option_type == 'call' 
                             else np.maximum(self.K - B_g, 0))
                
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