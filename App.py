from flask import Flask, jsonify, request, render_template
from Delta import fetch_options_data, get_spot_price_taifex, calculate_delta, current_time, datetime

app = Flask(__name__)

@app.route('/') # http://127.0.0.1:5000
def home():
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")  # 格式化當前時間
    return render_template('Index.html', current_time=current_time)

@app.route('/api/options', methods=['GET'])
def get_options():
    try:
        # 獲取台指期現貨價格
        spot_price = get_spot_price_taifex()
        
        # 爬取選擇權數據
        df = fetch_options_data()
        
        # 計算 Delta
        risk_free_rate = 0.02  # 無風險利率
        volatility = 0.25  # 波動率
        time_to_maturity_days = 7  # 到期日剩餘天數
        time_to_maturity = time_to_maturity_days / 365  # 轉換為年

        deltas = []
        for _, row in df.iterrows():
            option_type = "C" if row["買賣權"] == "C" else "P"
            strike_price = float(row["履約價"])
            delta = calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type)
            deltas.append(delta)

        df["Delta"] = deltas

        # 返回 JSON 格式
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
