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

# 剩餘時間（以年為單位）
def calculate_time_to_maturity(expiration_date):
    """動態計算剩餘到期時間。"""
    current_time = datetime.now()
    if isinstance(expiration_date, str):
        expiration_date = datetime.strptime(expiration_date, "%Y-%m-%dT%H:%M")
    delta = (expiration_date - current_time).total_seconds()  # 時間差（秒數）
    return max(delta / (365.25 * 24 * 3600), 0)  # 確保不會返回負數

# 動態更新的策略損益計算函數
def calculate_strategy_profit():
    # 參數設定
    S_range = np.linspace(23000, 25000, 2001)  # 標的價格範圍
    K = 24000  # 履約價格
    r = 0.015  # 無風險利率
    sigma = 0.2  # 年化波動率
    T_short_expiry = "2025-02-03T13:30"
    T_long_expiry = "2025-02-05T13:30"

    # 動態計算到期時間
    T_short = calculate_time_to_maturity(T_short_expiry)
    T_long = calculate_time_to_maturity(T_long_expiry)

    # 初始成本計算
    short_call_initial = [black_scholes(S, K, T_short, r, sigma, option_type="call") for S in S_range]
    long_call_initial = [black_scholes(S, K, T_long, r, sigma, option_type="call") for S in S_range]
    initial_cost = [long - short for long, short in zip(long_call_initial, short_call_initial)]

    # 到短期期限 (t = T_short) 的價值
    short_call_at_expiry = [max(S - K, 0) for S in S_range]  # 短期期權價值 (t = T_short)
    long_call_at_tshort = [black_scholes(S, K, T_long - T_short, r, sigma, option_type="call") for S in S_range]

    # 策略損益計算
    profits = [long_value - short_value - cost for long_value, short_value, cost in zip(long_call_at_tshort, short_call_at_expiry, initial_cost)]
    return S_range, profits

# 繪圖函數
def plot_strategy_profit():
    S_range, profits = calculate_strategy_profit()
    plt.figure(figsize=(10, 6))
    plt.plot(S_range, profits, label="Time Spread Profit")
    plt.axhline(0, color="black", linestyle="--", linewidth=1)
    plt.title(f"Time Spread Strategy Profit/Loss (Updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    plt.xlabel("Underlying Price (S)")
    plt.ylabel("Profit/Loss")
    plt.legend()
    plt.grid()

    # 標註重要價格點
    K = 24000  # Strike price
    plt.axvline(K, color="red", linestyle="--", label=f"Strike Price (K = {K})")
    plt.text(K, max(profits) * 0.5, f"K={K}", color="red", horizontalalignment='right')

    plt.show()

# 呼叫繪圖函數
plot_strategy_profit()