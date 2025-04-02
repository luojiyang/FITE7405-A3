import numpy as np
import matplotlib.pyplot as plt
from arithmetic_asian_option import arithmetic_asian_option_mc
from arithmetic_basket_option import arithmetic_basket_option_mc

import matplotlib
matplotlib.use('TkAgg')  # 可以尝试 'QtAgg' 等其他后端
import matplotlib.pyplot as plt

# 亚洲期权测试数据
asian_test_cases = [
    # (S0, K, T, sigma, r, m)
    (100, 100, 3, 0.3, 0.05, 100000),
    (100, 100, 3, 0.4, 0.05, 100000),
    # 可以添加更多测试用例
]

# 篮子期权测试数据
basket_test_cases = [
    # (S0_1, S0_2, K, sigma_1, sigma_2, rho, T, r, m)
    (100, 100, 100, 0.3, 0.3, 0.5, 3, 0.05, 100000),
    (100, 100, 100, 0.3, 0.3, 0.9, 3, 0.05, 100000),
    # 可以添加更多测试用例
]

# 测试亚洲期权并记录结果
asian_results = []
for case in asian_test_cases:
    price, _ = arithmetic_asian_option_mc(*case)
    asian_results.append(price)

# 测试篮子期权并记录结果
basket_results = []
for case in basket_test_cases:
    price = arithmetic_basket_option_mc(*case)
    basket_results.append(price)

# 绘制结果图
plt.figure(figsize=(12, 6))

# 亚洲期权结果图
plt.subplot(1, 2, 1)
plt.bar(range(len(asian_results)), asian_results)
plt.title('Arithmetic Asian Option Prices')
plt.xlabel('Test Case Index')
plt.ylabel('Option Price')
plt.xticks(range(len(asian_results)))

# 篮子期权结果图
plt.subplot(1, 2, 2)
plt.bar(range(len(basket_results)), basket_results)
plt.title('Arithmetic Basket Option Prices')
plt.xlabel('Test Case Index')
plt.ylabel('Option Price')
plt.xticks(range(len(basket_results)))

plt.tight_layout()
plt.show()
