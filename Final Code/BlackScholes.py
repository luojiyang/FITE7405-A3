import numpy as np
from scipy.stats import norm


class BlackScholesPricer:
    def __init__(
        self, S=100.0, K=100.0, T=1.0, sigma=0.2, r=0.05, q=0.0, option_type="call"
    ):
        """
        Black-Scholes option pricing calculator

        Parameters:
            S (float): Current price of the underlying asset (default: 100.0)
            K (float): Strike price (default: 100.0)
            T (float): Time to maturity (in years) (default: 1.0)
            sigma (float): Volatility (default: 0.2)
            r (float): Risk-free interest rate (default: 0.05)
            q (float): Continuous dividend yield/repo rate (default: 0.0)
            option_type (str): Option type ('call' or 'put') (default: 'call')
        """
        self.S = S
        self.K = K
        self.T = T
        self.sigma = sigma
        self.r = r
        self.q = q
        self.option_type = option_type

        # Validate parameters
        self._validate_parameters()

        # Precompute intermediate variables
        self.d1, self.d2 = self.calculate_d1_d2()

    def _validate_parameters(self):
        """Validate input parameters"""
        if self.S <= 0:
            raise ValueError("The underlying asset price S must be greater than 0")
        if self.K <= 0:
            raise ValueError("The strike price K must be greater than 0")
        if self.T <= 0:
            raise ValueError("The time to maturity T must be greater than 0")
        if self.sigma <= 0:
            raise ValueError("The volatility sigma must be greater than 0")
        if self.option_type.lower() not in ["call", "put"]:
            raise ValueError("option_type must be 'call' or 'put'")

        self.option_type = self.option_type.lower()

    def calculate_d1_d2(self):
        """
        Calculate d1 and d2 parameters for Black-Scholes model with repo rate

        Parameters:
        S (float): Spot price of the asset
        K (float): Strike price
        T (float): Time to maturity (in years)
        sigma (float): Volatility
        r (float): Risk-free interest rate
        q (float): Repo rate (dividend yield for stocks)
        """
        d1 = (np.log(self.S / self.K) + ((self.r - self.q) * self.T)) / (
            self.sigma * np.sqrt(self.T)
        ) + 0.5 * self.sigma * np.sqrt(self.T)
        d2 = (np.log(self.S / self.K) + ((self.r - self.q) * self.T)) / (
            self.sigma * np.sqrt(self.T)
        ) - 0.5 * self.sigma * np.sqrt(self.T)
        return d1, d2

    def call_value(self, d1, d2):
        """Calculate call option value using Black-Scholes formula with repo rate"""
        return self.S * np.exp(-self.q * self.T) * norm.cdf(d1) - self.K * np.exp(
            -self.r * self.T
        ) * norm.cdf(d2)

    def put_value(self, d1, d2):
        """Calculate put option value using Black-Scholes formula with repo rate"""
        return self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * np.exp(
            -self.q * self.T
        ) * norm.cdf(-d1)

    def calculate_option_price(self):
        """
        Calculate European option price using Black-Scholes model with repo rate

        Parameters:
        S (float): Spot price of the asset
        K (float): Strike price
        T (float): Time to maturity (in years)
        sigma (float): Volatility
        r (float): Risk-free interest rate
        q (float): Repo rate (dividend yield for stocks)
        option_type (str): 'call' or 'put'

        Returns:
        float: Option price
        """
        try:
            # Compute d1/d2 parameters
            d1, d2 = self.calculate_d1_d2()

            # Compute option price
            if self.option_type.lower() == "call":
                price = self.call_value(d1, d2)
            elif self.option_type.lower() == "put":
                price = self.put_value(d1, d2)
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'.")

            return {
                "price": price,
                "status": "success",
            }

        except Exception as e:
            return {
                "price": None,
                "status": "error",
                "message": f"Calculation failed: {str(e)}",
            }
