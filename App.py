import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from Delta import fetch_options_data, get_spot_price_taifex, calculate_delta, calculate_gamma, calculate_theta, calculate_vega, current_time, datetime, spot_price, calculate_days_to_maturity, volatility

app = Flask(__name__)
CORS(app)

# 從 JSON 文件中讀取到期日
with open("ExpirationDate.json", "r", encoding="utf-8") as file:
    expiration_data = json.load(file)
    expiration_date = datetime.fromisoformat(expiration_data["expiration_date"])

# 首頁路由，渲染模板
@app.route('/Index') # http://127.0.0.1:5000/Index
def home():
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")  # 格式化當前時間
    return render_template('Index.html', current_time=current_time, expiration_date=expiration_date.strftime("%Y-%m-%d %H:%M:%S"))

# 提供選擇權數據的 API
@app.route('/api/options', methods=['GET'])
def get_options():
    try:
        # 爬取選擇權數據
        df = fetch_options_data()

        # 獲取台指期現貨價格
        spot_price = get_spot_price_taifex()

        # 計算 Delta
        risk_free_rate = 0.02  # 無風險利率
        time_to_maturity_days = calculate_days_to_maturity(expiration_date)
        time_to_maturity = time_to_maturity_days / 365

        deltas = []
        for _, row in df.iterrows():
            option_type = "C" if row["買賣權"] == "C" else "P"
            strike_price = float(row["履約價"])
            delta = calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type)
            deltas.append(delta)

        df["Delta"] = deltas

        #計算 Gamma
        gammas = []
        for _, row in df.iterrows():
            strike_price = float(row["履約價"])
            gamma = calculate_gamma(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility)
            gammas.append(gamma)

        df["Gamma"] = gammas

        #計算 Theta
        thetas = []
        for _, row in df.iterrows():
            strike_price = float(row["履約價"])
            theta = calculate_theta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type)
            thetas.append(theta)
        
        df["Theta"] = thetas

        #計算 Vega
        vegas = []
        for _, row in df.iterrows():
            strike_price = float(row["履約價"])
            vega = calculate_gamma(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility * 100)
            vegas.append(vega)
        
        df["Vega"] = vegas

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

        # 返回 JSON 格式
        # 包括 spot_price 一起返回
        return jsonify({"spot_price": spot_price, "options": df.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 提供台指期現貨價格的 API
@app.route('/api/spot_price', methods=['GET'])
def get_spot_price():
    try:
        spot_price = get_spot_price_taifex()
        return jsonify({"spot_price": spot_price})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 提供到期日剩餘天數的 API
@app.route('/api/time_to_maturity', methods=['GET'])
def get_time_to_maturity():
    try:
        time_to_maturity_days = calculate_days_to_maturity(expiration_date)
        return jsonify({"time_to_maturity_days": time_to_maturity_days})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
