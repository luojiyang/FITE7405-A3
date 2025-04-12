import numpy as np
from scipy.stats import norm
import sobol_seq

class KIKOPutPricer:
    def __init__(self, S0=100, sigma=0.2, r=0.05, T=1.0, K=100, L=80, U=120, n=50, R=10, num_paths=100000):
        """
        KIKO Put Option Pricer
        Parameters:
            S0: Initial asset price (default 100)
            sigma: Volatility (default 0.2)
            r: Risk-free rate (default 0.05)
            T: Time to expiration (years) (default 1.0)
            K: Strike price (default 100)
            L: Lower knock-in barrier (default 80)
            U: Upper knock-out barrier (default 120)
            n: Number of observations (default 50)
            R: Discount amount when knocking out (default 10)
            num_paths: Number of simulation paths (default 100,000)
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
        
        # Validation parameters
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Verify that the input parameters are reasonable"""
        if self.L >= self.S0:
            raise ValueError("Lower knock-in barrier L must be less than the initial price S0")
        if self.U <= self.S0:
            raise ValueError("Upper knock-out barrier U must be greater than the initial price S0")
        if self.T <= 0:
            raise ValueError("Expiration time T must be greater than 0")
        if self.n <= 0:
            raise ValueError("Number of observations n must be greater than 0")
            
    def generate_sobol_paths(self):
        """Generating asset price paths using Sobol sequences"""
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
        """Calculating KIKO Put Option Price and Delta"""
        try:
            # Caculate price
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
            
            # Caculate Delta
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
        """Auxiliary method for price calculation in Delta calculation"""
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