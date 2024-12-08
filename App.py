from flask import Flask, jsonify, request, render_template
from Delta import fetch_options_data, calculate_delta, get_spot_price_taifex
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 啟用全局 CORS

@app.route('/')
def home():
    return render_template("Index.html")  # 前端頁面

@app.route('/api/deltas', methods=['GET'])
def get_options_data():
    try:
        # 參數
        risk_free_rate = float(request.args.get("risk_free_rate", 0.02))
        volatility = float(request.args.get("volatility", 0.25))
        time_to_maturity_days = int(request.args.get("time_to_maturity_days", 7))
        time_to_maturity = time_to_maturity_days / 365
        
        # 現貨價格
        spot_price = get_spot_price_taifex()
        
        # 爬取數據
        df = fetch_options_data()
        
        # 計算 Delta
        deltas = []
        for _, row in df.iterrows():
            option_type = "C" if row["買賣權"] == "C" else "P"
            strike_price = float(row["履約價"])
            delta = calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility, option_type)
            deltas.append(delta)
        
        df["Delta"] = deltas
        return jsonify({"status": "success", "data": df.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)