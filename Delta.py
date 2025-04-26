# 套件匯入
import requests as r
import pandas as pd
import json
from math import log, sqrt, exp # log 是以e為底
from scipy.stats import norm
from datetime import datetime, time, timedelta

# 反推隱含波動率 (IV) 的函數
# 若數值為 0.2，則表示年化波動率為 20% ， 日波動率 = 0.2 / sqrt(365)
def implied_volatility(option_price, spot_price, strike_price, time_to_maturity, risk_free_rate, option_type="C", tol=1e-5, max_iterations=100):
    lower_vol = 1e-6 # 隱含波動率搜尋的最小值（通常設為極小的正數，如 1e-6），避免除以零。
    upper_vol = 10.0 # 代表 隱含波動率 搜尋的最大值 1000% 年化波動率
    for _ in range(max_iterations):
        mid_vol = (lower_vol + upper_vol) / 2
        try:
            d1 = (log(spot_price / strike_price) + (risk_free_rate + 0.5 * mid_vol ** 2) * time_to_maturity) / (mid_vol * sqrt(time_to_maturity))
            d2 = d1 - mid_vol * sqrt(time_to_maturity)
            if option_type == "C":
                price = spot_price * norm.cdf(d1) - strike_price * exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
            else:
                price = strike_price * exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
        except Exception:
            return ""
        if abs(price - option_price) < tol:
            return mid_vol
        if price > option_price:
            upper_vol = mid_vol
        else:
            lower_vol = mid_vol
    return mid_vol

# spot_price = 即時價格
# strike_price = 履約價
# risk_free_rate = 無風險利率(連續複利)
# volatility = 隱含波動率
# time_to_maturity = 到期時間

# Black-Scholes 模型計算 Delta 的函數
def calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type="C"):
    d1 = (log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * sqrt(time_to_maturity))
    #d2 = d1 - volatility * sqrt(time_to_maturity)
    if option_type == "C":  # Call 選擇權
        return norm.cdf(d1) # 常態分布 的 累積分布函數 ( avg = 0, sd = 1 )
    elif option_type == "P":  # Put 選擇權
        return norm.cdf(d1) - 1
    else:
        raise ValueError("option_type 必須為 'C' 或 'P'")

# Black-Scholes 模型計算 Gamma 的函數
def calculate_gamma(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility):
    d1 = (log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * sqrt(time_to_maturity))
    return norm.pdf(d1) / (spot_price * volatility * sqrt(time_to_maturity))

# Black-Scholes 模型計算 Theta 的函數
def calculate_theta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type="C"):
    d1 = (log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * sqrt(time_to_maturity))
    d2 = d1 - volatility * sqrt(time_to_maturity)
    if option_type == "C":  # Call 選擇權
        return (-spot_price * norm.pdf(d1) * volatility / (2 * sqrt(time_to_maturity)) - risk_free_rate * strike_price * exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2))
    elif option_type == "P":  # Put 選擇權
        return (-spot_price * norm.pdf(d1) * volatility / (2 * sqrt(time_to_maturity)) + risk_free_rate * strike_price * exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2))
    else:
        raise ValueError("option_type 必須為 'C' 或 'P'")
    
# Black-Scholes 模型計算 Vega 的函數
def calculate_vega(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility):
    d1 = (log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * sqrt(time_to_maturity))
    return spot_price * norm.pdf(d1) * sqrt(time_to_maturity)


# 判斷最近的交易日
def get_last_trading_day(current_date):
    """
    計算最近的一個交易日
    :param current_date: datetime 對象，表示當前日期
    :return: 最近的一個交易日的日期
    """

    # 若是週六，返回週五
    if current_date.weekday() == 5:  # 週六
        return current_date - timedelta(days=1)
    # 若是週日，返回上週五
    elif current_date.weekday() == 6:  # 週日
        return current_date - timedelta(days=2)
    # 其他情況
    else:
        return current_date

# 將 CTime 轉換為 Y/MM/DD HH:MM:SS 格式
def convert_to_custom_timestamp(row):
    time_str = row["最新交易時間"]
    if not time_str or len(time_str) != 6:
        return ""  # 如果時間無效，返回空值
    
    # 提取交易時間
    hours = int(time_str[:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:6])
    trade_time = time(hours, minutes, seconds)

    # 獲取當前系統的日期
    system_today = datetime.today()
    system_time = datetime.now().time() # 格式 = 03:58:47.445722

    # 基於 system_time 判斷交易日期
    if system_time >= time(15, 0):  # 下午盤後交易
        trade_date = get_last_trading_day(system_today.date())
    elif system_time <= time(8, 30):  # 凌晨盤後交易
        trade_date = get_last_trading_day((system_today - timedelta(days=1)).date())
    else:  # 日間交易
        trade_date = system_today.date()
    
    # 組合 最新交易 的 完整時間
    # formatted_datetime = datetime.combine(trade_date, trade_time)
    formatted_str =  f"{trade_date.year}/{trade_date.month:02}/{trade_date.day:02} {trade_time}" #formatted_datetime.strftime("%Y/%m/%d %H:%M:%S")
    return formatted_str # Y/MM/DD hh:mm:ss

# 從 JSON 文件中讀取到期日
with open("Adjust.json", "r", encoding="utf-8") as file:
    expiration_data = json.load(file)
    expiration_date = datetime.fromisoformat(expiration_data["expiration_date"])
    expire_month = expiration_data["ExpireMonth"]

# 爬取 台指選擇權資料 的函數
def fetch_options_data(market_type="0"):
    url = "https://mis.taifex.com.tw/futures/api/getQuoteListOption"
    payload = {
        "MarketType": market_type,
        "SymbolType": "O",
        "KindID": "1",
        "CID": "TXO",
        "ExpireMonth": expire_month,  # 替換為你需要的到期月份 格式 = 202406W4(for週選); 202407(for月選)
        "RowSize": "全部",
        "PageNo": "",
        "SortColumn": "",
        "AscDesc": "A"
    }
    res = r.post(url, json=payload)
    data = res.json()
    df = pd.DataFrame(data['RtData']['QuoteList'])

    # 選取相關欄位
    # DataFrame
    df = df[["DispCName", "StrikePrice", "CP", "CBidPrice1", "CAskPrice1", "CLastPrice", "CRefPrice", "CTime"]]
    df.columns = ["商品名稱", "履約價", "買賣權", "買進價格", "賣出價格", "最新成交價", "昨日收盤價格", "最新交易時間"]

    # 將 "CTime" 轉換為 64 位格式
    df["最新交易時間64位"] = df.apply(convert_to_custom_timestamp, axis=1)

    return df

# spot_price 爬取台指期的資料
def get_spot_price_taifex(market_type="0"):
    url = "https://mis.taifex.com.tw/futures/api/getQuoteList"
    payload = {"MarketType": market_type,
           "SymbolType":"F",
           "KindID":"1",
           #"CID": "TXO", # 為了找近週小台的資料, 不限制商品代碼
           "ExpireMonth":"",
           "RowSize":"全部",
           "PageNo":"",
           "SortColumn":"",
           "AscDesc":"A"}
    res = r.post(url, json=payload)
    data = res.json()

    try:
        # 確保數據不為空並可轉換為浮點數
        # data['RtData']['QuoteList'][0] : 台指現貨 (加權指數)
        # data['RtData']['QuoteList'][1] : 台指期近月
        # data['RtData']['QuoteList'][7] : 小台現貨 (加權指數)
        # data['RtData']['QuoteList'][8] : 近週小台
        spot_price_str = data['RtData']['QuoteList'][8]['CLastPrice']
        if not spot_price_str or not spot_price_str.strip():
            raise ValueError("Spot price data is empty or invalid.")
        spot_price = float(spot_price_str)
        return spot_price
    except (IndexError, KeyError, ValueError) as e:
        print(f"Error retrieving spot price: {e}")
        return None  # 或設定為默認值，例如 return 0.0


# time_to_maturity_days 計算
def calculate_days_to_maturity(expiration_date):
    today = datetime.now()
    dt = expiration_date - today
    return max((dt.total_seconds()) / ( 24 * 60 * 60 ), 0)  # 確保剩餘天數不為負 且 資料型態type 為 float

time_to_maturity_days = calculate_days_to_maturity(expiration_date)
time_to_maturity = time_to_maturity_days / 365

print("到期天數 =", calculate_days_to_maturity(expiration_date))
print("到期日 =", expiration_date)

'''
# volatility 爬取波動率的資料
def get_volatility():
    url = "https://mis.taifex.com.tw/futures/api/getQuoteListVIX"
    payload = {"SortColumn":"",
                "AscDesc":"A"}
    res = r.post(url, json=payload)
    data = res.json()
    volatility = float(data['RtData']['QuoteList'][0]['CLastPrice'])
    return volatility

volatility = get_volatility() / 100 # 如果沒有資料 會回傳錯誤訊息
print(f"台指選波動率指數: {volatility}")
'''


# 主程式
def main():
    # 根據當前時間自動判斷盤別
    now = datetime.now()
    now_time = now.time()
    if time(8, 30, 0) <= now_time < time(15, 0, 0):
        session_type = "0"  # 日盤
    else:
        # 15:00:00 ~ 23:59:59 或 00:00:00 ~ 05:00:00
        if now_time >= time(15, 0, 0) or now_time < time(8, 30, 0):
            session_type = "1"  # 夜盤
        else:
            session_type = "0"  # 其他時間預設日盤

    risk_free_rate = 0.02  # 無風險利率 2%
    # volatility = 0.25  # 波動率 25%
    # time_to_maturity_days = 7  # 到期日剩餘天數（7天）
    # time_to_maturity = time_to_maturity_days / 365  # 轉換為年

    # 爬取台指期現貨價格
    spot_price = get_spot_price_taifex(market_type=session_type)
    if spot_price is None:
        print("Error: Unable to retrieve spot price. Exiting program.")
        return  # 停止執行或根據需要進行其他處理
    
    # 爬取台指期數據
    
    spot_price = get_spot_price_taifex(market_type=session_type) # 如果沒有資料 會回傳錯誤訊息
    print(f"近週小台價格: {spot_price}")
    
    # 爬取選擇權數據
    df = fetch_options_data(market_type=session_type)

    # 確保 df 不為空
    if df.empty:
        print("Error: No options data retrieved.")
        return
    
    # 計算漲跌幅 並加入 DataFrame
    difference_prices = []
    for _, row in df.iterrows():
        try:
            # 確保數據存在 且 可轉換為浮點數
            reference_price = float(row["昨日收盤價格"]) if row["昨日收盤價格"] else None
            last_price = float(row["最新成交價"]) if row["最新成交價"] else None
            
            if reference_price is not None and last_price is not None:
                # 計算漲跌幅
                difference_price = last_price - reference_price
                difference_prices.append(difference_price)
            else:
                # 若數據缺失，設為 NaN 或默認值
                difference_prices.append("")
        except ValueError:
            # 捕獲無法轉換為浮點數的情況
            difference_prices.append("")

    # 將 漲跌幅 新增為 DataFrame 欄位
    df["漲跌幅"] = difference_prices

    # 計算 IV 並用平均值覆蓋 volatility
    ivs = []
    for _, row in df.iterrows():
        try:
            option_type = "C" if row["買賣權"] == "C" else "P"
            strike_price = float(row["履約價"])
            last_price = float(row["最新成交價"])
            if last_price > 0 and spot_price > 0 and strike_price > 0 and time_to_maturity > 0:
                iv = implied_volatility(
                    option_price=last_price,
                    spot_price=spot_price,
                    strike_price=strike_price,
                    time_to_maturity=time_to_maturity,
                    risk_free_rate=risk_free_rate,
                    option_type=option_type
                )
            else:
                iv = ""
        except Exception:
            iv = ""
        ivs.append(iv)
    df["IV"] = ivs

    # 用所有有效 IV 的平均值覆蓋 volatility，若無有效IV則用 0.3
    valid_ivs = [iv for iv in ivs if isinstance(iv, float) and iv > 0]
    if valid_ivs:
        volatility_used = sum(valid_ivs) / len(valid_ivs)
    else:
        volatility_used = 0.3

    # 計算 Delta 並加入 DataFrame
    deltas = []
    for _, row in df.iterrows():
        option_type = "C" if row["買賣權"] == "C" else "P"
        strike_price = float(row["履約價"])
        delta = calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used, option_type)
        deltas.append(delta)
    df["Delta"] = deltas

    # 計算 Gamma 並加入 DataFrame
    gammas = []
    for _, row in df.iterrows():
        strike_price = float(row["履約價"])
        gamma = calculate_gamma(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used)
        gammas.append(gamma)
    df["Gamma"] = gammas

    # 計算 Theta 並加入 DataFrame
    thetas = []
    for _, row in df.iterrows():
        option_type = "C" if row["買賣權"] == "C" else "P"
        strike_price = float(row["履約價"])
        theta = calculate_theta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used, option_type)
        thetas.append(theta)
    df["Theta"] = thetas

    # 計算 Vega 並加入 DataFrame
    vegas = []
    for _, row in df.iterrows():
        strike_price = float(row["履約價"])
        vega = calculate_vega(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used)
        vegas.append(vega)
    df["Vega"] = vegas


    # 顯示 DataFrame 結果
    print(df)

# 執行主程式
if __name__ == "__main__":
    main()

# 當前時間
current_time = datetime.now()
print("當前時間 =", current_time)
