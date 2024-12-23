# 套件匯入
import requests as r
import pandas as pd
from math import log, sqrt # log 是以e為底
from scipy.stats import norm
from datetime import datetime, time, timedelta

# Black-Scholes 模型計算 Delta 的函數
# spot_price = 即時價格
# strike_price = 履約價
# risk_free_rate = 無風險利率(連續複利)
# volatility = 隱含波動率
# time_to_maturity = 到期時間

def calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type="C"):
    d1 = (log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * sqrt(time_to_maturity))
    #d2 = d1 - volatility * sqrt(time_to_maturity)
    if option_type == "C":  # Call 選擇權
        return norm.cdf(d1) # 常態分布 的 累積分布函數 ( avg = 0, sd = 1 )
    elif option_type == "P":  # Put 選擇權
        return norm.cdf(d1) - 1
    else:
        raise ValueError("option_type 必須為 'C' 或 'P'")

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
    if system_time >= time(13, 45):  # 下午盤後交易
        trade_date = get_last_trading_day(system_today.date())
    elif system_time <= time(8, 45):  # 凌晨盤後交易
        trade_date = get_last_trading_day((system_today - timedelta(days=1)).date())
    else:  # 日間交易
        trade_date = system_today.date()
    
    # 組合 最新交易 的 完整時間
    # formatted_datetime = datetime.combine(trade_date, trade_time)
    formatted_str =  f"{trade_date.year}/{trade_date.month:02}/{trade_date.day:02} {trade_time}" #formatted_datetime.strftime("%Y/%m/%d %H:%M:%S")
    return formatted_str # Y/MM/DD hh:mm:ss

# 爬取 台指選擇權資料 的函數
def fetch_options_data():
    url = "https://mis.taifex.com.tw/futures/api/getQuoteListOption"
    payload = {
        "MarketType": "0",
        "SymbolType": "O",
        "KindID": "1",
        "CID": "TXO",
        "ExpireMonth": "202412W4",  # 替換為你需要的到期月份 格式 = 202406W4(for週選); 202407(for月選)
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
def get_spot_price_taifex():
    url = "https://mis.taifex.com.tw/futures/api/getQuoteList"
    payload = {"MarketType":"0",
           "SymbolType":"F",
           "KindID":"1",
           "CID":"TXF",
           "ExpireMonth":"",
           "RowSize":"全部",
           "PageNo":"",
           "SortColumn":"",
           "AscDesc":"A"}
    res = r.post(url, json=payload)
    data = res.json()
    spot_price = float(data['RtData']['QuoteList'][1]['CLastPrice'])  # 取第2筆資料
    return spot_price
    #return data

spot_price = get_spot_price_taifex() # 如果沒有資料 會回傳錯誤訊息
print(f"台指期近月價格: {spot_price}")

# time_to_maturity_days 計算
def calculate_days_to_maturity(expiration_date):
    today = datetime.now()
    dt = expiration_date - today
    return max((dt.total_seconds()) / (24*60*60), 0)  # 確保剩餘天數不為負 且 資料型態type 為 float

expiration_date = datetime(2024, 12, 25, 13, 30)  # 到期日
time_to_maturity_days = calculate_days_to_maturity(expiration_date)
time_to_maturity = time_to_maturity_days / 365

print("到期天數 =", calculate_days_to_maturity(expiration_date))
print("到期日 =", expiration_date)

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
print(f"台指選波動率: {volatility}")
    


# 主程式
def main():
    # 參數設定
    #spot_price = 22277  # 當前現貨價格 (替換為動態價格爬取)
    risk_free_rate = 0.02  # 無風險利率 2% (通常是國債利率)
    # volatility = 0.25  # 波動率 25%
    #time_to_maturity_days = 7  # 到期日剩餘天數（7天）
    #time_to_maturity = time_to_maturity_days / 365  # 轉換為年

    # 爬取選擇權數據
    df = fetch_options_data()

    # 計算 Delta 並加入 DataFrame
    deltas = []
    for _, row in df.iterrows():
        option_type = "C" if row["買賣權"] == "C" else "P"
        strike_price = float(row["履約價"])
        delta = calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type)
        deltas.append(delta)

    # 將 Delta 新增為 DataFrame 欄位
    df["Delta"] = deltas

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

    # 顯示 DataFrame 結果
    print(df)

# 執行主程式
if __name__ == "__main__":
    main()

# 當前時間
current_time = datetime.now()
print("當前時間 =", current_time)
