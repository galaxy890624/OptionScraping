import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from Delta import (
    fetch_options_data, get_spot_price_taifex, calculate_delta, calculate_gamma,
    calculate_theta, calculate_vega, implied_volatility, calculate_days_to_maturity, datetime, time
)

app = Flask(__name__)
CORS(app)

# 從 Adjust.json 讀取到期日與到期月份
with open("Adjust.json", "r", encoding="utf-8") as file:
    expiration_data = json.load(file)
    expiration_date = datetime.fromisoformat(expiration_data["expiration_date"])
    expire_month = expiration_data["ExpireMonth"]

@app.route('/Index')
def home():
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    return render_template('Index.html', current_time=current_time, expiration_date=expiration_date.strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/api/options', methods=['GET'])
def get_options():
    try:
        # 根據當前時間自動判斷盤別
        now = datetime.now()
        now_time = now.time()
        if time(8, 30, 0) <= now_time < time(15, 0, 0):
            session_type = "0"  # 日盤
        else:
            # 15:00:00 ~ 23:59:59 或 00:00:00 ~ 08:29:59
            session_type = "1"  # 夜盤

        # 爬取選擇權數據
        df = fetch_options_data(market_type=session_type)
        # 獲取台指期現貨價格
        spot_price = get_spot_price_taifex(market_type=session_type)
        risk_free_rate = 0.02
        time_to_maturity_days = calculate_days_to_maturity(expiration_date)
        time_to_maturity = time_to_maturity_days / 365

        # 計算漲跌幅
        difference_prices = []
        for _, row in df.iterrows():
            try:
                reference_price = float(row["昨日收盤價格"]) if row["昨日收盤價格"] else None
                last_price = float(row["最新成交價"]) if row["最新成交價"] else None
                if reference_price is not None and last_price is not None:
                    difference_price = last_price - reference_price
                    difference_prices.append(difference_price)
                else:
                    difference_prices.append("")
            except ValueError:
                difference_prices.append("")
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
        valid_ivs = [iv for iv in ivs if isinstance(iv, float) and iv > 0]
        if valid_ivs:
            volatility_used = sum(valid_ivs) / len(valid_ivs)
        else:
            volatility_used = 0.3

        # 計算 Delta
        deltas = []
        for _, row in df.iterrows():
            option_type = "C" if row["買賣權"] == "C" else "P"
            strike_price = float(row["履約價"])
            delta = calculate_delta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used, option_type)
            deltas.append(delta)
        df["Delta"] = deltas

        # 計算 Gamma
        gammas = []
        for _, row in df.iterrows():
            strike_price = float(row["履約價"])
            gamma = calculate_gamma(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used)
            gammas.append(gamma)
        df["Gamma"] = gammas

        # 計算 Theta
        thetas = []
        for _, row in df.iterrows():
            option_type = "C" if row["買賣權"] == "C" else "P"
            strike_price = float(row["履約價"])
            theta = calculate_theta(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used, option_type)
            thetas.append(theta)
        df["Theta"] = thetas

        # 計算 Vega
        vegas = []
        for _, row in df.iterrows():
            strike_price = float(row["履約價"])
            vega = calculate_vega(spot_price, strike_price, time_to_maturity, risk_free_rate, volatility_used)
            vegas.append(vega)
        df["Vega"] = vegas

        return jsonify({"spot_price": spot_price, "options": df.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/spot_price', methods=['GET'])
def get_spot_price():
    try:
        now = datetime.now()
        now_time = now.time()
        if time(8, 30, 0) <= now_time < time(15, 0, 0):
            session_type = "0"
        else:
            session_type = "1"
        spot_price = get_spot_price_taifex(market_type=session_type)
        return jsonify({"spot_price": spot_price})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/time_to_maturity', methods=['GET'])
def get_time_to_maturity():
    try:
        time_to_maturity_days = calculate_days_to_maturity(expiration_date)
        return jsonify({"time_to_maturity_days": time_to_maturity_days})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
