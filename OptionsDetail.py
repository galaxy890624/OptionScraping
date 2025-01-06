import requests
import pandas as pd
import logging
from typing import Optional
from datetime import datetime, time

logger = logging.getLogger(__name__)

start_time = datetime.time()
def fetch_options_detail_data() -> Optional[pd.DataFrame]:
    """
    獲取期權交易詳情數據
    返回: DataFrame 或 None（如果發生錯誤）
    """
    url = "https://openapi.taifex.com.tw/v1/OptionsTimeAndSalesData"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            logger.warning("API returned empty data")
            return None
            
        df = pd.DataFrame(data)
        required_columns = ["ProductCode", "ContractMonth(Week)", "StrikePrice", 
                          "CallPut", "TradePrice", "Volume(BorS)", "Date", "TimeOfTrades"]
        
        if not all(col in df.columns for col in required_columns):
            logger.error("Missing required columns in API response")
            return None
            
        # 數據轉換
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
            # 將時間轉換為字符串格式 HH:MM:SS
            df['TimeOfTrades'] = pd.to_datetime(df['TimeOfTrades'], format='%H%M%S').dt.strftime('%H:%M:%S')
            df['TradePrice'] = pd.to_numeric(df['TradePrice'], errors='coerce')
            df['Volume(BorS)'] = pd.to_numeric(df['Volume(BorS)'], errors='coerce')
            
            # 將日期轉換為字符串格式 YYYY-MM-DD
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"Error converting data types: {str(e)}")
            return None
            
        # 處理缺失值
        df = df.dropna(subset=['TradePrice', 'Volume(BorS)'])
        
        # 重命名列
        column_mapping = {
            "ProductCode": "商品名稱",
            "ContractMonth(Week)": "到期月份(週)",
            "StrikePrice": "履約價",
            "CallPut": "買賣權",
            "TradePrice": "成交價",
            "Volume(BorS)": "成交量",
            "Date": "交易日期",
            "TimeOfTrades": "交易時間",
        }
        df.rename(columns=column_mapping, inplace=True)

        # 篩選商品名稱為 TXO 且 到期月份(週) 為 202501W2 的資料
        df = df[(df["商品名稱"] == "TXO") & (df["到期月份(週)"] == "202501W2")]

        # 調整列順序
        column_order = ["商品名稱", "到期月份(週)", "履約價", "買賣權", "成交價", "成交量", "交易日期", "交易時間"]
        df = df[column_order]
        
        logger.info(f"Successfully fetched and processed {len(df)} records")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None
    
end_time = datetime.time()
execute_time = end_time - start_time
print(fetch_options_detail_data())
print(execute_time)