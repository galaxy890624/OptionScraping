import requests
import pandas as pd
import logging
from typing import Optional
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

start_time = datetime.now()

def fetch_options_detail_data(product_code: str, contract_month: str) -> Optional[pd.DataFrame]:
    """
    獲取並過濾期權交易詳情數據，僅保留指定商品名稱和到期月份的資料。
    
    Args:
        product_code (str): 商品名稱，例如 'TXO'
        contract_month (str): 到期月份（週），例如 '202501W2'
    
    Returns:
        Optional[pd.DataFrame]: 篩選後的 DataFrame 或 None（如果發生錯誤）
    """
    url = "https://openapi.taifex.com.tw/v1/OptionsTimeAndSalesData"
    
    try:
        # 獲取數據
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.warning("API returned empty data")
            return None

        # 轉換為 DataFrame 並篩選
        df = pd.DataFrame(data)
        df = df[(df["ProductCode"] == product_code) & (df["ContractMonth(Week)"] == contract_month)]
        
        if df.empty:
            logger.warning("No matching data found for the given filters")
            return None

        # 數據處理
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
        df['TimeOfTrades'] = pd.to_datetime(df['TimeOfTrades'], format='%H%M%S').dt.strftime('%H:%M:%S')
        df['TradePrice'] = pd.to_numeric(df['TradePrice'], errors='coerce')
        df['Volume(BorS)'] = pd.to_numeric(df['Volume(BorS)'], errors='coerce')

        # 清理和重命名欄位
        df = df.dropna(subset=['TradePrice', 'Volume(BorS)'])  # 移除無效資料
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

        # 調整列順序
        column_order = ["商品名稱", "到期月份(週)", "履約價", "買賣權", "成交價", "成交量", "交易日期", "交易時間"]
        df = df[column_order]

        logger.info(f"Successfully fetched and processed {len(df)} records")
        return df
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except ValueError as e:
        logger.error(f"Data conversion error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

# 主程式執行
if __name__ == "__main__":
    # 設置篩選條件
    product_code = "TXO"
    contract_month = "202501"
    
    # 獲取篩選後的數據
    df = fetch_options_detail_data(product_code, contract_month)
    
    if df is not None:
        print(df)
    else:
        print("No data found or an error occurred.")

end_time = datetime.now()
execute_time = end_time - start_time
print("執行時間 =", execute_time)

'''
PS D:\python\OptionScraping> python OptionsDetail.py    
INFO:__main__:Successfully fetched and processed 338663 records
       商品名稱   到期月份(週)    履約價 買賣權  成交價  成交量        交易日期      交易時間
1267    TXO  202501W2  20500   P  1.1    1  2025-01-03  08:49:17
1268    TXO  202501W2  20500   P  1.1    1  2025-01-03  08:49:17
1269    TXO  202501W2  20500   P  0.9    5  2025-01-03  09:15:21
1270    TXO  202501W2  20500   P  0.9    5  2025-01-03  09:15:21
1271    TXO  202501W2  20500   P  0.9   14  2025-01-03  09:20:39
...     ...       ...    ...  ..  ...  ...         ...       ...
380766  TXO  202501W2  25600   C  0.1    1  2025-01-03  13:27:40
380767  TXO  202501W2  25600   C  0.2    1  2025-01-03  13:34:29
380768  TXO  202501W2  25600   C  0.2    1  2025-01-03  13:34:29
380791  TXO  202501W2  25700   C  9.9    1  2025-01-03  09:08:46
380792  TXO  202501W2  25700   C  9.9    1  2025-01-03  09:08:46

[338663 rows x 8 columns]
執行時間 = 0:02:08.659247
'''