from flask import Flask, jsonify, render_template
import requests
import pandas as pd
from OptionsDetail import fetch_options_detail_data

app = Flask(__name__)

# 定義 API URL
API_URL = "https://openapi.taifex.com.tw/v1/OptionsTimeAndSalesData"

@app.route('/')
def home():
    return render_template("OptionsDetail.html")  # 渲染前端首頁

@app.route('/api/options_detail', methods=['GET'])
def options_detail():
    try:

        # 將數據轉換為 DataFrame
        df = fetch_options_detail_data()

        # 處理數據類型
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')  # 日期轉換
        df['TimeOfTrades'] = pd.to_datetime(df['TimeOfTrades'], format='%H%M%S').dt.time  # 時間轉換
        df['TradePrice'] = pd.to_numeric(df['TradePrice'], errors='coerce')  # 價格轉換為浮點數
        df['Volume(BorS)'] = pd.to_numeric(df['Volume(BorS)'], errors='coerce')  # 成交量轉換為整數

        # 重命名列
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

        # 調整列順序
        column_order = ["商品名稱", "到期月份(週)", "履約價", "買賣權", "成交價", "成交量", "交易日期", "交易時間"]
        df = df[column_order]

        # 返回 JSON 格式
        return jsonify({"options_detail": df.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)