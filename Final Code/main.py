import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from BlackScholes import BlackScholesPricer
from ImpliedVolatility import ImpliedVolatility
from BinomialTree import BinomialTreePricer
from GeometricAsian import GeometricAsianPricer
from ArithmeticAsian import ArithmeticAsianPricer
from GeometricBasket import GeometricBasketPricer
from ArithmeticBasket import ArithmeticBasketPricer
from KIKO import KIKOPutPricer

class OptionPricerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FITE7405 Option Pricer")
        self.root.geometry("1250x1000")
        
        # Apply ttkbootstrap light theme
        self.style = tb.Style(theme="cosmo")
        
        # Create main container
        self.main_frame = tb.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header = tb.Label(
            self.main_frame, 
            text="Option Pricer", 
            font=('Helvetica', 18, 'bold'),
            bootstyle=PRIMARY
        )
        self.header.pack(pady=(0, 15))
        
        # Create notebook for different option types
        self.notebook = tb.Notebook(self.main_frame, bootstyle=PRIMARY)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each option type
        self.create_european_frame()
        self.create_implied_vol_frame()
        self.create_american_frame()
        self.create_geometric_asian_frame()
        self.create_arithmetic_asian_frame()
        self.create_geometric_basket_frame()
        self.create_arithmetic_basket_frame()
        self.create_kiko_frame()
        
        # Output area
        self.output_frame = tb.Frame(self.main_frame)
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.output_text = tb.Text(
            self.output_frame, 
            height=10, 
            wrap=tk.WORD,
            font=('Consolas', 10),
            background='#ffffff',
            foreground='#000000'
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tb.Scrollbar(
            self.output_frame, 
            command=self.output_text.yview,
            bootstyle=ROUND
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status = tb.Label(
            self.main_frame,
            text="Ready",
            bootstyle=(SECONDARY, INVERSE),
            anchor=tk.W
        )
        self.status.pack(fill=tk.X, pady=(5, 0))
        
    def create_input_field(self, frame, label_text, var, row, default_value, tooltip=None):
        """Helper function to create consistent input fields"""
        lbl = tb.Label(frame, text=label_text, bootstyle=PRIMARY)
        lbl.grid(row=row, column=0, padx=5, pady=5, sticky=tk.E)
        
        entry = tb.Entry(frame, textvariable=var, bootstyle=PRIMARY)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
        var.set(default_value)
        
        if tooltip:
            tb.ToolTip(entry, text=tooltip, bootstyle=(INFO, INVERSE))
        
        return entry

    def create_european_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="European Option")
        
        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.euro_S0 = tk.DoubleVar()
        self.euro_sigma = tk.DoubleVar()
        self.euro_r = tk.DoubleVar()
        self.euro_q = tk.DoubleVar()
        self.euro_T = tk.DoubleVar()
        self.euro_K = tk.DoubleVar()
        self.euro_type = tk.StringVar()

        self.create_input_field(container, "Spot Price (S0):", self.euro_S0, 0, 100)
        self.create_input_field(container, "Volatility (σ):", self.euro_sigma, 1, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.euro_r, 2, 0.05)
        self.create_input_field(container, "Repo Rate (q):", self.euro_q, 3, 0.0)
        self.create_input_field(container, "Time to Maturity (T):", self.euro_T, 4, 3)
        self.create_input_field(container, "Strike Price (K):", self.euro_K, 5, 100)
        
        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]  # Define options explicitly
        option_menu = tb.OptionMenu(
            container, 
            self.euro_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        self.euro_type.set("Call")

        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_bs_price,
            bootstyle=SUCCESS
        )
        btn.grid(row=7, column=0, columnspan=2, pady=10)

    def calculate_bs_price(self):
        """Calculate Black-Scholes option price"""
        try:
            params = {
                'S': self.euro_S0.get(),
                'K': self.euro_K.get(),
                'T': self.euro_T.get(),
                'sigma': self.euro_sigma.get(),
                'r': self.euro_r.get(),
                'q': self.euro_q.get(),
                'option_type': self.euro_type.get()
            }

            pricer = BlackScholesPricer(**params)
            
            # Calculate price
            result = pricer.calculate_option_price()
            
            if result['status'] == 'success':
                # Format result text
                result_text = (
                    f"Black-Scholes Calculation Results:\n"
                    f"Spot Price (S): {params['S']}\n"
                    f"Strike Price (K): {params['K']}\n"
                    f"Time to Maturity (T): {params['T']}\n"
                    f"Volatility (σ): {params['sigma']}\n"
                    f"Risk-free Rate (r): {params['r']}\n"
                    f"Option Type: {params['option_type']}\n\n"
                    f"Option Price: {result['price']:.4f}\n"
                    f"{'-'*50}"
                )

                # Show detailed result in output text box
                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)  # Auto-scroll to end
                
                self.status.config(text="Calculation completed successfully", bootstyle=SUCCESS)
            else:
                error_msg = f"Error: {result['message']}"
                self.output_text.insert(tk.END, f"Black-Scholes Error: {error_msg}\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except Exception as e:
            error_msg = f"Error in Black-Scholes calculation: {str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation failed", bootstyle=DANGER)        
    
    def create_implied_vol_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="Implied Volatility")
        
        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.iv_S0 = tk.DoubleVar()
        self.iv_r = tk.DoubleVar()
        self.iv_q = tk.DoubleVar()
        self.iv_T = tk.DoubleVar()
        self.iv_K = tk.DoubleVar()
        self.iv_premium = tk.DoubleVar()
        self.iv_type = tk.StringVar()

        self.create_input_field(container, "Spot Price (S0):", self.iv_S0, 0, 100)
        self.create_input_field(container, "Risk-free Rate (r):", self.iv_r, 1, 0.05)
        self.create_input_field(container, "Repo Rate (q):", self.iv_q, 2, 0.0)
        self.create_input_field(container, "Time to Maturity (T):", self.iv_T, 3, 3)
        self.create_input_field(container, "Strike Price (K):", self.iv_K, 4, 100)
        self.create_input_field(container, "Option Premium:", self.iv_premium, 5, 20)

        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]
        option_menu = tb.OptionMenu(
            container, 
            self.iv_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        self.iv_type.set("Call")

        btn = tb.Button(
            container, 
            text="Calculate Implied Volatility", 
            command=self.calculate_implied_volatility,
            bootstyle=SUCCESS
        )
        btn.grid(row=7, column=0, columnspan=2, pady=10)

    def calculate_implied_volatility(self):
        """Calculating Implied Volatility"""
        try:
            params = {
                'S': self.iv_S0.get(),
                'K': self.iv_K.get(),
                'T': self.iv_T.get(),
                'r': self.iv_r.get(),
                'q': self.iv_q.get(),
                'option_premium': self.iv_premium.get(),
                'option_type': self.iv_type.get().lower()
            }

            calculator = ImpliedVolatility(**params)

            result = calculator.calculate_implied_vol()

            if result['status'] == 'converged':
                result_text = (
                    f"Implied Volatility Calculation Results:\n"
                    f"Spot Price (S): {params['S']:.2f}\n"
                    f"Strike Price (K): {params['K']:.2f}\n"
                    f"Time to Maturity (T): {params['T']:.2f}\n"
                    f"Risk-free Rate (r): {params['r']:.4f}\n"
                    f"Repo Rate (q): {params['q']:.4f}\n"
                    f"Option Premium: {params['option_premium']:.2f}\n"
                    f"Option Type: {params['option_type']}\n\n"
                    f"Implied Volatility: {result['implied_vol']:.6f}\n"
                    f"Iterations: {result['iterations']}\n"
                    f"{'-'*50}"
                )

                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Implied volatility calculated successfully", bootstyle=SUCCESS)
                
            elif result['status'] == 'max_iter_reached':
                result_text = (
                    f"Implied Volatility Calculation Warning:\n"
                    f"Maximum iterations reached ({result['iterations']})\n"
                    f"Approximate Volatility: {result['implied_vol']:.6f}\n"
                    f"Error: {result.get('message', 'Not fully converged')}\n"
                    f"{'-'*50}"
                )
                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation did not fully converge", bootstyle=WARNING)
                
            else:
                error_msg = f"Implied Volatility Calculation Error:\n{result.get('message', 'Unknown error')}\n{'-'*50}"
                self.output_text.insert(tk.END, error_msg + "\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except ValueError as e:
            error_msg = f"Input Error in Implied Volatility Calculation:\n{str(e)}\n{'-'*50}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Invalid input parameters", bootstyle=DANGER)
            
        except Exception as e:
            error_msg = f"System Error in Implied Volatility Calculation:\n{str(e)}\n{'-'*50}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation error occurred", bootstyle=DANGER)
       
    def create_american_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="American Option")
        
        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.amer_S0 = tk.DoubleVar()
        self.amer_sigma = tk.DoubleVar()
        self.amer_r = tk.DoubleVar()
        self.amer_T = tk.DoubleVar()
        self.amer_K = tk.DoubleVar()
        self.amer_N = tk.IntVar()
        self.amer_type = tk.StringVar()
        
        self.create_input_field(container, "Spot Price (S0):", self.amer_S0, 0, 100)
        self.create_input_field(container, "Volatility (σ):", self.amer_sigma, 1, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.amer_r, 2, 0.05)
        self.create_input_field(container, "Time to Maturity (T):", self.amer_T, 3, 3)
        self.create_input_field(container, "Strike Price (K):", self.amer_K, 4, 100)
        self.create_input_field(container, "Number of Steps (N):", self.amer_N, 5, 100)

        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]
        option_menu = tb.OptionMenu(
            container, 
            self.amer_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        self.amer_type.set("Call")

        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_american_price,
            bootstyle=SUCCESS
        )
        btn.grid(row=7, column=0, columnspan=2, pady=10)
    
    def calculate_american_price(self):
        """Calculating American Option Prices"""
        try:
            params = {
                'S': self.amer_S0.get(),
                'sigma': self.amer_sigma.get(),
                'r': self.amer_r.get(),
                'T': self.amer_T.get(),
                'K': self.amer_K.get(),
                'n': self.amer_N.get(),
                'optionType': self.amer_type.get()
            }

            pricer = BinomialTreePricer(**params)

            result = pricer.calculate_price()
            
            if result['status'] == 'success':
                result_text = (
                    f"American Option Calculation Results:\n"
                    f"Spot Price (S0): {params['S']}\n"
                    f"Volatility (σ): {params['sigma']}\n"
                    f"Risk-free Rate (r): {params['r']}\n"
                    f"Time to Maturity (T): {params['T']}\n"
                    f"Strike Price (K): {params['K']}\n"
                    f"Number of Steps (N): {params['n']}\n"
                    f"Option Type: {params['optionType']}\n\n"
                    f"American {params['optionType']} Price: {result['price']:.4f}\n"
                    f"{'-'*50}"
                )

                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation completed successfully", bootstyle=SUCCESS)
            else:
                error_msg = f"Error: {result['message']}"
                self.output_text.insert(tk.END, f"American Option Calculation Error: {error_msg}\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except Exception as e:
            error_msg = f"Error in American Option calculation: {str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation failed", bootstyle=DANGER)
    
    def create_geometric_asian_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="Geometric Asian")
        
        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.geo_asian_S0 = tk.DoubleVar()
        self.geo_asian_sigma = tk.DoubleVar()
        self.geo_asian_r = tk.DoubleVar()
        self.geo_asian_T = tk.DoubleVar()
        self.geo_asian_K = tk.DoubleVar()
        self.geo_asian_n = tk.IntVar()
        self.geo_asian_type = tk.StringVar()
        
        self.create_input_field(container, "Spot Price (S0):", self.geo_asian_S0, 0, 100)
        self.create_input_field(container, "Volatility (σ):", self.geo_asian_sigma, 1, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.geo_asian_r, 2, 0.05)
        self.create_input_field(container, "Time to Maturity (T):", self.geo_asian_T, 3, 3)
        self.create_input_field(container, "Strike Price (K):", self.geo_asian_K, 4, 100)
        self.create_input_field(container, "Number of Observations (n):", self.geo_asian_n, 5, 50)

        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]
        option_menu = tb.OptionMenu(
            container, 
            self.geo_asian_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        self.geo_asian_type.set("Call")

        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_geometric_asian,
            bootstyle=SUCCESS
        )
        btn.grid(row=7, column=0, columnspan=2, pady=10)

    def calculate_geometric_asian(self):
        """Calculating Geometric Asian Option Prices"""
        try:
            params = {
                'S': self.geo_asian_S0.get(),
                'K': self.geo_asian_K.get(),
                'T': self.geo_asian_T.get(),
                'sigma': self.geo_asian_sigma.get(),
                'r': self.geo_asian_r.get(),
                'n': self.geo_asian_n.get(),
                'option_type': self.geo_asian_type.get().lower()
            }

            pricer = GeometricAsianPricer(**params)

            result = pricer.calculate_price()
            
            if result['status'] == 'success':
                output_text = (
                    f"Geometric Asian Option Results:\n"
                    f"Spot Price (S): {params['S']:.2f}\n"
                    f"Strike Price (K): {params['K']:.2f}\n"
                    f"Time to Maturity (T): {params['T']:.2f}\n"
                    f"Volatility (σ): {params['sigma']:.4f}\n"
                    f"Risk-free Rate (r): {params['r']:.4f}\n"
                    f"Observations (n): {params['n']}\n"
                    f"Option Type: {params['option_type']}\n\n"
                    f"Calculated Price: {result['price']:.4f}\n"
                    f"Adjusted Volatility (σ̂): {result['parameters']['sigma_hat']:.6f}\n"
                    f"Adjusted Drift (μ̂): {result['parameters']['miu_hat']:.6f}\n"
                    f"{'-'*50}"
                )

                self.output_text.insert(tk.END, output_text + "\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation completed", bootstyle=SUCCESS)
                
            else:
                error_msg = f"Calculation Error: {result['message']}"
                self.output_text.insert(tk.END, error_msg + "\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except ValueError as e:
            error_msg = f"Input Error: {str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Invalid input", bootstyle=DANGER)
            
        except Exception as e:
            error_msg = f"System Error: {str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation error", bootstyle=DANGER)  

    def create_arithmetic_asian_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="Arithmetic Asian")

        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.ari_asian_S0 = tk.DoubleVar()
        self.ari_asian_sigma = tk.DoubleVar()
        self.ari_asian_r = tk.DoubleVar()
        self.ari_asian_T = tk.DoubleVar()
        self.ari_asian_K = tk.DoubleVar()
        self.ari_asian_n = tk.IntVar()
        self.ari_asian_m = tk.IntVar()
        self.ari_asian_cv = tk.StringVar()
        self.ari_asian_type = tk.StringVar()
        
        self.create_input_field(container, "Spot Price (S0):", self.ari_asian_S0, 0, 100)
        self.create_input_field(container, "Volatility (σ):", self.ari_asian_sigma, 1, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.ari_asian_r, 2, 0.05)
        self.create_input_field(container, "Time to Maturity (T):", self.ari_asian_T, 3, 3)
        self.create_input_field(container, "Strike Price (K):", self.ari_asian_K, 4, 100)
        self.create_input_field(container, "Number of Observations (n):", self.ari_asian_n, 5, 50)
        self.create_input_field(container, "Number of Paths (m):", self.ari_asian_m, 6, 100000)

        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=7, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]
        option_menu = tb.OptionMenu(
            container, 
            self.ari_asian_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        self.ari_asian_type.set("Call")

        tb.Label(container, text="Control Variate:", bootstyle=PRIMARY).grid(
            row=8, column=0, padx=5, pady=5, sticky=tk.E)
        cv_options = ["None", "Geometric Asian"]
        cv_menu = tb.OptionMenu(
            container, 
            self.ari_asian_cv, 
            cv_options[1],
            *cv_options,
            bootstyle=PRIMARY
        )
        cv_menu.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)

        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_arithmetic_asian_price,
            bootstyle=SUCCESS
        )
        btn.grid(row=9, column=0, columnspan=2, pady=10)

    def calculate_arithmetic_asian_price(self):
            """Calculate Arithmetic Asian option price"""
            try:
                params = {
                    'S0': self.ari_asian_S0.get(),
                    'sigma': self.ari_asian_sigma.get(),
                    'r': self.ari_asian_r.get(),
                    'T': self.ari_asian_T.get(),
                    'K': self.ari_asian_K.get(),
                    'n': self.ari_asian_n.get(),
                    'm': self.ari_asian_m.get(),
                    'option_type': self.ari_asian_type.get().lower(),
                    'control_variate': self.ari_asian_cv.get()
                }
                print(params)
                pricer = ArithmeticAsianPricer(**params)

                result = pricer.calculate_price()
                
                if result['status'] == 'success':
                    result_text = (
                        f"Arithmetic Asian {params['option_type'].capitalize()} Calculation Results:\n"
                        f"Spot Price (S0): {params['S0']}\n"
                        f"Volatility (σ): {params['sigma']}\n"
                        f"Risk-free Rate (r): {params['r']}\n"
                        f"Time to Maturity (T): {params['T']}\n"
                        f"Strike Price (K): {params['K']}\n"
                        f"Number of Observations (n): {params['n']}\n"
                        f"Number of Paths (m): {params['m']}\n"
                        f"Option Type: {params['option_type'].capitalize()}\n"
                        f"Control Variate: {self.ari_asian_cv.get()}\n\n"
                        f"Price: {result['price']:.4f}\n"
                        f"95% Confidence Interval: [{result['conf_interval'][0]:.4f}, {result['conf_interval'][1]:.4f}]\n"
                        f"{'-'*50}"
                    )

                    self.output_text.insert(tk.END, result_text + "\n\n")
                    self.output_text.see(tk.END)
                    
                    self.status.config(text="Calculation completed successfully", bootstyle=SUCCESS)
                else:
                    error_msg = f"Error: {result['message']}"
                    self.output_text.insert(tk.END, f"Arithmetic Asian Calculation Error: {error_msg}\n\n")
                    self.output_text.see(tk.END)
                    self.status.config(text="Calculation failed", bootstyle=DANGER)
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.output_text.insert(tk.END, f"Arithmetic Asian Calculation Error: {error_msg}\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)

    def create_geometric_basket_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="Geometric Basket")

        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.geo_basket_S1 = tk.DoubleVar()
        self.geo_basket_S2 = tk.DoubleVar()
        self.geo_basket_sigma1 = tk.DoubleVar()
        self.geo_basket_sigma2 = tk.DoubleVar()
        self.geo_basket_r = tk.DoubleVar()
        self.geo_basket_T = tk.DoubleVar()
        self.geo_basket_K = tk.DoubleVar()
        self.geo_basket_rho = tk.DoubleVar()
        self.geo_basket_type = tk.StringVar()

        self.create_input_field(container, "Spot Price Asset 1 (S1):", self.geo_basket_S1, 0, 100)
        self.create_input_field(container, "Spot Price Asset 2 (S2):", self.geo_basket_S2, 1, 100)
        self.create_input_field(container, "Volatility Asset 1 (σ1):", self.geo_basket_sigma1, 2, 0.3)
        self.create_input_field(container, "Volatility Asset 2 (σ2):", self.geo_basket_sigma2, 3, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.geo_basket_r, 4, 0.05)
        self.create_input_field(container, "Time to Maturity (T):", self.geo_basket_T, 5, 3)
        self.create_input_field(container, "Strike Price (K):", self.geo_basket_K, 6, 100)
        self.create_input_field(container, "Correlation (ρ):", self.geo_basket_rho, 7, 0.5)

        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=8, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]
        option_menu = tb.OptionMenu(
            container, 
            self.geo_basket_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
        self.geo_basket_type.set("Call")

        # 计算按钮放在row=9
        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_geometric_basket,
            bootstyle=SUCCESS
        )
        btn.grid(row=9, column=0, columnspan=2, pady=10)

    def calculate_geometric_basket(self):
        """Calculating Geometric Basket Option Prices"""
        try:
            params = {
                'S_1': self.geo_basket_S1.get(),
                'S_2': self.geo_basket_S2.get(),
                'sigma_1': self.geo_basket_sigma1.get(),
                'sigma_2': self.geo_basket_sigma2.get(),
                'r': self.geo_basket_r.get(),
                'T': self.geo_basket_T.get(),
                'K': self.geo_basket_K.get(),
                'rho': self.geo_basket_rho.get(),
                'optionType': self.geo_basket_type.get()
            }

            pricer = GeometricBasketPricer(**params)

            result = pricer.calculate_price()
            
            if result['status'] == 'success':
                result_text = (
                    f"Geometric Basket Calculation Results:\n"
                    f"Spot Price 1 (S1): {params['S_1']}\n"
                    f"Spot Price 2 (S2): {params['S_2']}\n"
                    f"Volatility 1 (σ1): {params['sigma_1']}\n"
                    f"Volatility 2 (σ2): {params['sigma_2']}\n"
                    f"Risk-free Rate (r): {params['r']}\n"
                    f"Time to Maturity (T): {params['T']}\n"
                    f"Strike Price (K): {params['K']}\n"
                    f"Correlation (ρ): {params['rho']}\n"
                    f"Option Type: {params['optionType']}\n\n"
                    f"Geometric Basket {params['optionType']} Price: {result['price']:.4f}\n"
                    f"{'-'*50}"
                )

                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)

                self.status.config(text="Calculation completed successfully", bootstyle=SUCCESS)
            else:
                error_msg = f"Error: {result['message']}"
                self.output_text.insert(tk.END, f"Geometric Basket Calculation Error: {error_msg}\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except Exception as e:
            error_msg = f"Error in Geometric Basket calculation: {str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation failed", bootstyle=DANGER)
     
    def create_arithmetic_basket_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="Arithmetic Basket")

        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.ari_basket_S1 = tk.DoubleVar()
        self.ari_basket_S2 = tk.DoubleVar()
        self.ari_basket_sigma1 = tk.DoubleVar()
        self.ari_basket_sigma2 = tk.DoubleVar()
        self.ari_basket_r = tk.DoubleVar()
        self.ari_basket_T = tk.DoubleVar()
        self.ari_basket_K = tk.DoubleVar()
        self.ari_basket_rho = tk.DoubleVar()
        self.ari_basket_m = tk.IntVar()
        self.ari_basket_cv = tk.StringVar()
        self.ari_basket_type = tk.StringVar()

        self.create_input_field(container, "Spot Price Asset 1 (S1):", self.ari_basket_S1, 0, 100)
        self.create_input_field(container, "Spot Price Asset 2 (S2):", self.ari_basket_S2, 1, 100)
        self.create_input_field(container, "Volatility Asset 1 (σ1):", self.ari_basket_sigma1, 2, 0.3)
        self.create_input_field(container, "Volatility Asset 2 (σ2):", self.ari_basket_sigma2, 3, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.ari_basket_r, 4, 0.05)
        self.create_input_field(container, "Time to Maturity (T):", self.ari_basket_T, 5, 3)
        self.create_input_field(container, "Strike Price (K):", self.ari_basket_K, 6, 100)
        self.create_input_field(container, "Correlation (ρ):", self.ari_basket_rho, 7, 0.5)
        self.create_input_field(container, "Number of Paths (m):", self.ari_basket_m, 8, 100000)

        tb.Label(container, text="Option Type:", bootstyle=PRIMARY).grid(
            row=9, column=0, padx=5, pady=5, sticky=tk.E)
        option_types = ["Call", "Put"]
        option_menu = tb.OptionMenu(
            container, 
            self.ari_basket_type, 
            option_types[0],
            *option_types,
            bootstyle=PRIMARY
        )
        option_menu.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)
        self.ari_basket_type.set("Call")

        # Control Variate放在row=10
        tb.Label(container, text="Control Variate:", bootstyle=PRIMARY).grid(
            row=10, column=0, padx=5, pady=5, sticky=tk.E)
        cv_options = ["None", "Geometric Basket"]
        cv_menu = tb.OptionMenu(
            container, 
            self.ari_basket_cv, 
            cv_options[1],
            *cv_options,
            bootstyle=PRIMARY
        )
        cv_menu.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)

        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_arithmetic_basket_price,
            bootstyle=SUCCESS
        )
        btn.grid(row=11, column=0, columnspan=2, pady=10)

    def calculate_arithmetic_basket_price(self):
        """Calculate Arithmetic Basket option price"""
        try:
            params = {
                'S0_1': self.ari_basket_S1.get(),
                'S0_2': self.ari_basket_S2.get(),
                'sigma_1': self.ari_basket_sigma1.get(),
                'sigma_2': self.ari_basket_sigma2.get(),
                'rho': self.ari_basket_rho.get(),
                'r': self.ari_basket_r.get(),
                'T': self.ari_basket_T.get(),
                'K': self.ari_basket_K.get(),
                'option_type': self.ari_basket_type.get().lower(),
                'm': self.ari_basket_m.get(),
                'control_variate': self.ari_basket_cv.get()
            }

            pricer = ArithmeticBasketPricer(**params)

            result = pricer.calculate_price()
            
            if result['status'] == 'success':
                result_text = (
                    f"Arithmetic Basket {params['option_type'].capitalize()} Calculation Results:\n"
                    f"Spot Price Asset 1 (S1): {params['S0_1']}\n"
                    f"Spot Price Asset 2 (S2): {params['S0_2']}\n"
                    f"Volatility Asset 1 (σ1): {params['sigma_1']}\n"
                    f"Volatility Asset 2 (σ2): {params['sigma_2']}\n"
                    f"Correlation (ρ): {params['rho']}\n"
                    f"Risk-free Rate (r): {params['r']}\n"
                    f"Time to Maturity (T): {params['T']}\n"
                    f"Strike Price (K): {params['K']}\n"
                    f"Number of Paths (m): {params['m']}\n"
                    f"Option Type: {params['option_type'].capitalize()}\n"
                    f"Control Variate: {self.ari_basket_cv.get()}\n\n"
                    f"Price: {result['price']:.4f}\n"
                    f"95% Confidence Interval: [{result['conf_interval'][0]:.4f}, {result['conf_interval'][1]:.4f}]\n"
                    f"{'-'*50}"
                )

                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)
                
                self.status.config(text="Calculation completed successfully", bootstyle=SUCCESS)
            else:
                error_msg = f"Error: {result['message']}"
                self.output_text.insert(tk.END, f"Arithmetic Basket Calculation Error: {error_msg}\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.output_text.insert(tk.END, f"Arithmetic Basket Calculation Error: {error_msg}\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation failed", bootstyle=DANGER)
   
    def create_kiko_frame(self):
        frame = tb.Frame(self.notebook)
        self.notebook.add(frame, text="KIKO Put")

        container = tb.Frame(frame)
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.kiko_S0 = tk.DoubleVar()
        self.kiko_sigma = tk.DoubleVar()
        self.kiko_r = tk.DoubleVar()
        self.kiko_T = tk.DoubleVar()
        self.kiko_K = tk.DoubleVar()
        self.kiko_L = tk.DoubleVar()
        self.kiko_U = tk.DoubleVar()
        self.kiko_n = tk.IntVar()
        self.kiko_R = tk.DoubleVar()
        
        self.create_input_field(container, "Spot Price (S0):", self.kiko_S0, 0, 100)
        self.create_input_field(container, "Volatility (σ):", self.kiko_sigma, 1, 0.3)
        self.create_input_field(container, "Risk-free Rate (r):", self.kiko_r, 2, 0.05)
        self.create_input_field(container, "Time to Maturity (T):", self.kiko_T, 3, 3)
        self.create_input_field(container, "Strike Price (K):", self.kiko_K, 4, 100)
        self.create_input_field(container, "Lower Barrier (L):", self.kiko_L, 5, 80)
        self.create_input_field(container, "Upper Barrier (U):", self.kiko_U, 6, 120)
        self.create_input_field(container, "Number of Observations (n):", self.kiko_n, 7, 50)
        self.create_input_field(container, "Rebate (R):", self.kiko_R, 8, 10)

        btn = tb.Button(
            container, 
            text="Calculate Price", 
            command=self.calculate_kiko_price,
            bootstyle=SUCCESS
        )
        btn.grid(row=9, column=0, columnspan=2, pady=10)

    def calculate_kiko_price(self):
        """Calculate KIKO option price"""
        try:
            params = {
                'S0': self.kiko_S0.get(),
                'sigma': self.kiko_sigma.get(),
                'r': self.kiko_r.get(),
                'T': self.kiko_T.get(),
                'K': self.kiko_K.get(),
                'L': self.kiko_L.get(),
                'U': self.kiko_U.get(),
                'n': self.kiko_n.get(),
                'R': self.kiko_R.get()
            }

            pricer = KIKOPutPricer(**params)

            result = pricer.calculate_price()
            
            if result['status'] == 'success':
                result_text = (
                    f"KIKO Put Calculation Results:\n"
                    f"Spot Price (S0): {params['S0']}\n"
                    f"Volatility (σ): {params['sigma']}\n"
                    f"Risk-free Rate (r): {params['r']}\n"
                    f"Time to Maturity (T): {params['T']}\n"
                    f"Strike Price (K): {params['K']}\n"
                    f"Lower Barrier (L): {params['L']}\n"
                    f"Upper Barrier (U): {params['U']}\n"
                    f"Number of Observations (n): {params['n']}\n"
                    f"Rebate (R): {params['R']}\n\n"
                    f"KIKO Put Price: {result['price']:.4f}\n"
                    f"95% Confidence Interval: [{result['conf_interval'][0]:.4f}, {result['conf_interval'][1]:.4f}]\n"
                    f"Delta: {result['delta']:.4f}\n"
                    f"{'-'*50}"
                )
                self.output_text.insert(tk.END, result_text + "\n\n")
                self.output_text.see(tk.END)
                
                self.status.config(text="Calculation completed successfully", bootstyle=SUCCESS)
            else:
                error_msg = f"Error: {result['message']}"
                self.output_text.insert(tk.END, f"KIKO Calculation Error: {error_msg}\n\n")
                self.output_text.see(tk.END)
                self.status.config(text="Calculation failed", bootstyle=DANGER)
                
        except Exception as e:
            error_msg = f"Error in KIKO calculation: {str(e)}"
            self.output_text.insert(tk.END, error_msg + "\n\n")
            self.output_text.see(tk.END)
            self.status.config(text="Calculation failed", bootstyle=DANGER)

# Main application
if __name__ == "__main__":
    root = tb.Window(themename="cosmo")  # Light theme
    app = OptionPricerGUI(root)
    root.mainloop()