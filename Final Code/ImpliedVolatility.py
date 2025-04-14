import numpy as np
from scipy.stats import norm


class ImpliedVolatility:
    def __init__(
        self,
        S=100.0,
        K=100.0,
        T=1.0,
        r=0.05,
        q=0.0,
        option_premium=None,
        option_type="call",
    ):
        """
        Implied Volatility

        Parameters:
            S (float): Current price of the underlying asset (default: 100.0)
            K (float): Strike price (default: 100.0)
            T (float): Time to maturity (in years) (default: 1.0)
            r (float): Risk-free interest rate (default: 0.05)
            q (float): Continuous dividend yield/repurchase rate (default: 0.0)
            option_type (str): Option type ('call' or 'put') (default: 'call')
            option_premium (float): Market price/premium of the option (default: None)
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
        """Parameter validation"""
        if not all(x > 0 for x in [self.S, self.K, self.T]):
            raise ValueError("S, K, T must be greater than 0")
        if self.option_type not in ["call", "put"]:
            raise ValueError("option_type must be 'call' or 'put'")
        if self.option_premium is not None and self.option_premium <= 0:
            raise ValueError("option_premium must be greater than 0")

    def _calculate_d1_d2(self, sigma):
        """Calculate d1 and d2 parameters (used for implied volatility calculation)"""
        d1 = np.log(self.S / self.K) + (self.r - self.q + 0.5 * sigma**2) * self.T
        d1 /= sigma * np.sqrt(self.T)
        d2 = d1 - sigma * np.sqrt(self.T)
        return d1, d2

    def calculate_price(self, sigma=None):
        """
        Calculate the option price

        Parameters:
            sigma (float): Specified volatility (default uses the initialized parameter)

        Returns:
            float: Theoretical option price
        """
        sigma = (
            sigma if sigma is not None else getattr(self, "sigma", 0.2)
        )  # default volatility 0.2
        d1, d2 = self._calculate_d1_d2(sigma)

        if self.option_type == "call":
            return self.S * np.exp(-self.q * self.T) * norm.cdf(d1) - self.K * np.exp(
                -self.r * self.T
            ) * norm.cdf(d2)
        else:
            return self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * np.exp(
                -self.q * self.T
            ) * norm.cdf(-d1)

    def calculate_implied_vol(self, max_iter=100000, tol=1e-6):
        """
        Calculate implied volatility (Newton's method)

        Parameters:
            max_iter (int): Maximum number of iterations (default: 100)
            tol (float): Convergence tolerance (default: 1e-6)

        Returns:
            dict: {
                'implied_vol': float,  # Implied volatility
                'iterations': int,     # Actual number of iterations
                'status': str          # 'converged'/'max_iter_reached'/'error'
                'message': str         # Error message (if any)
            }
        """
        if self.option_premium is None:
            return {
                "status": "error",
                "message": "option_premium (option market price) is not set",
            }

        try:
            # Initial guess (Manaster & Koehler method)
            sigma = np.sqrt(
                2
                * np.abs(
                    (np.log(self.S / self.K) + (self.r - self.q) * self.T) / self.T
                )
            )

            for i in range(max_iter):
                d1, d2 = self._calculate_d1_d2(sigma)

                # Calculate theoretical price and vega
                if self.option_type == "call":
                    price = self.S * np.exp(-self.q * self.T) * norm.cdf(
                        d1
                    ) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
                    vega = (
                        self.S
                        * np.exp(-self.q * self.T)
                        * norm.pdf(d1)
                        * np.sqrt(self.T)
                    )
                else:
                    price = self.K * np.exp(-self.r * self.T) * norm.cdf(
                        -d2
                    ) - self.S * np.exp(-self.q * self.T) * norm.cdf(-d1)
                    vega = (
                        self.S
                        * np.exp(-self.q * self.T)
                        * norm.pdf(d1)
                        * np.sqrt(self.T)
                    )

                # Check for convergence
                diff = price - self.option_premium
                if abs(diff) < tol:
                    return {
                        "implied_vol": sigma,
                        "iterations": i + 1,
                        "status": "converged",
                    }

                # Newton's method iteration (prevent division by zero)
                if vega < 1e-12:
                    break
                sigma -= diff / vega

            return {
                "implied_vol": sigma,
                "iterations": max_iter,
                "status": "max_iter_reached",
                "message": f"Maximum iterations {max_iter} reached (did not converge)",
            }

        except Exception as e:
            return {
                "implied_vol": None,
                "iterations": 0,
                "status": "error",
                "message": f"Calculation failed: {str(e)}",
            }
