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
        return norm.cdf(d1) # 常態分布 的 累積分布函數
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
    # 若是週一凌晨，返回上週五
    elif current_date.weekday() == 0 and datetime.now().time() < time(8, 45):  # 週一且時間在 0:00~08:45
        return current_date - timedelta(days=3)
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

# 爬取資料的函數
def fetch_options_data():
    url = "https://mis.taifex.com.tw/futures/api/getQuoteListOption"
    payload = {
        "MarketType": "0",
        "SymbolType": "O",
        "KindID": "1",
        "CID": "TXO",
        "ExpireMonth": "202412",  # 替換為你需要的到期月份 格式 = 202406W4(for週選); 202407(for月選)
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
    # 要用 data 的 資料
    '''
    以下是data的格式
    {'RtCode': '0', 'RtMsg': '', 'RtData': {'QuoteList': [{'SymbolID': 'TX420200K4-O', 'SpotID': '', 'DispCName': '臺指選W4114;20200買權', 'DispEName': 'TX4W4114;20200C', 'Status': 'TC', 'CBidPrice1': '2800.000', 'CBidSize1': '5', 'CAskPrice1': '2830.000', 'CAskSize1': '5', 'CTotalVolume': '', 'COpenPrice': '0.000', 'CHighPrice': '0.000', 'CLowPrice': '0.000', 'CLastPrice': '', 'CRefPrice': '2370.000', 'CCeilPrice': '4620.000', 'CFloorPrice': '115.000', 'CP': 'C', 'StrikePrice': '20200', 'SettlementPrice': '2810.000', 'OpenInterest': '0', 'CDate': '20241122', 'CTime': '', 'SpotWeights': '1.0', 'CTestTime': '', 'CBestBidPrice': '2800.000', 'CBestAskPrice': '2830.000', 'CBestBidSize': '5', 'CBestAskSize': '5'}, ...}
    '''
    df = df[["DispCName", "StrikePrice", "CP", "CBidPrice1", "CAskPrice1", "CLastPrice", "CTime"]]
    df.columns = ["商品名稱", "履約價", "買賣權", "買進價格", "賣出價格", "最新成交價", "最新交易時間"]

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
    '''
    以下是 data 的格式
    {'SymbolID': 'TXFL4-F', 'SpotID': '', 'DispCName': '臺指期124', 'DispEName': 'TX124', 'Status': '', 'CBidPrice1': '22183.00', 'CBidSize1': '10', 'CAskPrice1': '22185.00', 'CAskSize1': '4', 'CTotalVolume': '26918', 'COpenPrice': '22210.00', 'CHighPrice': '22221.00', 'CLowPrice': '22004.00', 'CLastPrice': '22185.00', 'CRefPrice': '22330.00', 'CCeilPrice': '24563.00', 'CFloorPrice': '20097.00', 'SettlementPrice': '', 'OpenInterest': '', 'CDate': '20241129', 'CTime': '092652', 'CTestTime': '084455', 'CDiff': '-145.00', 'CDiffRate': '-0.65', 'CAmpRate': '0.97', 'CBestBidPrice': '22183.00', 'CBestAskPrice': '22185.00', 'CBestBidSize': '10', 'CBestAskSize': '4', 'CTestPrice': '22216.00', 'CTestVolume': '201'}
    第1筆資料 = 加權指數(台指現貨)
    第2筆資料 = 近月
    第3筆資料 = 次月
    通常是用第2筆資料
    '''
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

expiration_date = datetime(2024, 12, 18, 13, 30)  # 到期日
time_to_maturity_days = calculate_days_to_maturity(expiration_date)
time_to_maturity = time_to_maturity_days / 365

print("到期日 =", calculate_days_to_maturity(expiration_date))
print("到期天數 =", expiration_date)

# 主程式
def main():
    # 參數設定
    #spot_price = 22277  # 當前現貨價格 (替換為動態價格爬取)
    risk_free_rate = 0.02  # 無風險利率 2% (通常是國債利率)
    volatility = 0.25  # 波動率 25%
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
    #return df.to_dict(orient="records")

    # 顯示 DataFrame 結果
    print(df)

# 執行主程式
if __name__ == "__main__":
    main()

# 當前時間
current_time = datetime.now()
print("當前時間 =", current_time)