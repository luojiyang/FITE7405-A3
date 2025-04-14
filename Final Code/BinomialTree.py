import numpy as np


class BinomialTreePricer:
    def __init__(
        self, S=100, K=100, T=1.0, sigma=0.2, r=0.05, n=100, optionType="call"
    ):
        """
        Binomial Tree Option Pricer

        Parameters:
            S: Current stock price (default 100)
            K: Strike price (default 100)
            T: Time to maturity (in years) (default 1.0)
            sigma: Volatility (default 0.2)
            r: Risk-free interest rate (default 0.05)
            n: Number of steps (default 100)
            optionType: Option type 'call' or 'put' (default 'call')
        """
        self.S = S
        self.K = K
        self.T = T
        self.sigma = sigma
        self.r = r
        self.n = n
        self.optionType = optionType.lower()

        # Validate parameters
        self._validate_parameters()

        # Compute commonly used variables
        self.delta_t = T / n
        self.u = np.exp(sigma * np.sqrt(self.delta_t))
        self.d = 1 / self.u
        self.p = (np.exp(r * self.delta_t) - self.d) / (self.u - self.d)
        self.df = np.exp(-r * self.delta_t)

    def _validate_parameters(self):
        """Validate input parameters"""
        if self.S <= 0:
            raise ValueError("Current stock price S must be greater than 0")
        if self.K <= 0:
            raise ValueError("Strike price K must be greater than 0")
        if self.T <= 0:
            raise ValueError("Time to maturity T must be greater than 0")
        if self.sigma <= 0:
            raise ValueError("Volatility sigma must be greater than 0")
        if self.n <= 0:
            raise ValueError("Number of steps n must be greater than 0")
        if self.optionType not in ["call", "put"]:
            raise ValueError("optionType must be 'call' or 'put'")

    def calculate_price(self):
        """Calculate option price"""
        try:
            # Compute asset prices at maturity
            prices = np.zeros(self.n + 1)
            for i in range(self.n + 1):
                prices[i] = self.S * (self.u ** (self.n - i)) * (self.d**i)

            # Compute option values at maturity
            values = np.zeros(self.n + 1)
            if self.optionType == "call":
                for i in range(self.n + 1):
                    values[i] = max(0, prices[i] - self.K)
            elif self.optionType == "put":
                for i in range(self.n + 1):
                    values[i] = max(0, self.K - prices[i])

            # Backward induction to calculate option price
            for step in range(self.n - 1, -1, -1):
                for i in range(step + 1):
                    prices[i] = prices[i] / self.u
                    if self.optionType == "call":
                        values[i] = max(
                            0,
                            prices[i] - self.K,
                            self.df
                            * (self.p * values[i] + (1 - self.p) * values[i + 1]),
                        )
                    elif self.optionType == "put":
                        values[i] = max(
                            0,
                            self.K - prices[i],
                            self.df
                            * (self.p * values[i] + (1 - self.p) * values[i + 1]),
                        )

            price = values[0]

            return {"price": price, "status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
