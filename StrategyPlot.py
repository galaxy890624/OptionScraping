import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import datetime

# Black-Scholes期權定價公式
def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    return price

# 參數設定
'''
可替換以下參數
無風險利率 https://www.cnyes.com/bond/intLoan1.aspx
波動率 https://mis.taifex.com.tw/futures/VolatilityQuotes/
'''
S_range = np.linspace(23000, 25000, 500)  # 標的價格範圍
K = 24000  # 履約價格
r = 0.015  # 無風險利率
sigma = 0.2  # 年化波動率


# 剩餘時間（以年為單位）
def calculate_time_to_maturity(expiration_date):
    current_date = datetime(2025, 1, 19, 0, 0)
    expiration_date = datetime.strptime(expiration_date, "%Y-%m-%dT%H:%M")
    delta = (expiration_date - current_date).total_seconds()
    return delta / (365.25 * 24 * 3600)

# from t=0 to t=short
'''
example
operate time name price(t=0) price(t=short) profit
short 202409 5600sc 40 0 40-0
long 202410 5600bc  150 135 135-150
total               (40-0) + (135-150)

剩餘時間 t=0 t=short t=long
short calculate_time_to_maturity(T_short) 0 -
long calculate_time_to_maturity(T_long) calculate_time_to_maturity(T_long - T_short) 0
'''
T_short = calculate_time_to_maturity("2025-02-03T13:30")
T_long = calculate_time_to_maturity("2025-02-05T13:30")

# 初始成本計算
short_call_initial = [black_scholes(S, K, T_short, r, sigma, option_type="call") for S in S_range]
long_call_initial = [black_scholes(S, K, T_long, r, sigma, option_type="call") for S in S_range]
initial_cost = [long - short for long, short in zip(long_call_initial, short_call_initial)]

# 到短期期限 (t = T_short) 的價值
short_call_at_expiry = [max(S - K, 0) for S in S_range]  # 短期期權價值 (t = T_short)
long_call_at_tshort = [black_scholes(S, K, T_long - T_short, r, sigma, option_type="call") for S in S_range]

# 計算策略損益
# 買進 買權時間價差 LongCalendarSpread
# 1. 賣出202501w5(結算時間 = 2025-02-03T13:30)24000call
# 2. 買進202502w1(結算時間 = 2025-02-05T13:30)24000call
# 3. 短期結算時 就全部平倉
# 策略損益計算 (假設 t=short 時平倉)
profits = [long_value - short_value - cost for long_value, short_value, cost in zip(long_call_at_tshort, short_call_at_expiry, initial_cost)]

# 繪圖
plt.figure(figsize=(10, 6))
plt.plot(S_range, profits, label="Time Spread Profit")
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.title("Time Spread Strategy Profit/Loss")
plt.xlabel("Underlying Price (S)")
plt.ylabel("Profit/Loss")
plt.legend()
plt.grid()

# 標註重要價格點
plt.axvline(K, color="red", linestyle="--", label=f"Strike Price (K = {K})")
plt.text(K, max(profits) * 0.5, "K=24000", color="red", horizontalalignment='right')

plt.show()