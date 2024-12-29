import requests
import pandas as pd

# API URL
url = "https://openapi.taifex.com.tw/v1/DailyMarketReportOpt"

# 發送請求
response = requests.get(url)

if response.status_code == 200:
    # 解析數據
    data = response.json()
    
    # 將數據轉換為 DataFrame
    df = pd.DataFrame(data)
    
    # 處理數據類型
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')  # 日期轉換
    #df['TimeOfTrades'] = pd.to_datetime(df['TimeOfTrades'], format='%H%M%S').dt.time  # 時間轉換
    #df['TradePrice'] = pd.to_numeric(df['TradePrice'], errors='coerce')  # 價格轉換為浮點數
    #df['Volume(BorS)'] = pd.to_numeric(df['Volume(BorS)'], errors='coerce')  # 成交量轉換為整數
    
    # 新增列名稱（為了和要求順序對應）
    '''
    df.rename(
        columns={
            "ProductCode": "商品名稱",
            "ContractMonth(Week)": "到期月份(週)",
            "StrikePrice": "履約價",
            "CallPut": "買賣權",
            "TradePrice": "成交價",
            "Volume(BorS)": "成交量",
            "Date": "交易日期",
            "TimeOfTrades": "交易時間",
        },
        inplace=True
    )
    '''
    
    
    # 調整列順序
    # column_order = ["商品名稱", "到期月份(週)", "履約價", "買賣權", "成交價", "成交量", "交易日期", "交易時間"]
    # df = df[column_order]
    
    # 顯示調整後的 DataFrame
    print(df)

else:
    print(f"Error: {response.status_code}")