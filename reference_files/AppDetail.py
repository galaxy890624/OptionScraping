from flask import Flask, jsonify, render_template
import logging
from logging.handlers import RotatingFileHandler
from OptionsDetail import fetch_options_detail_data

app = Flask(__name__)

# 設置日誌
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)

@app.route('/')
def home():
    return render_template("OptionsDetail.html")

@app.route('/api/options_detail', methods=['GET'])
def get_options_detail():
    try:
        df = fetch_options_detail_data()
        if df is None or df.empty:
            app.logger.error("No data received from options detail API")
            return jsonify({"error": "無法獲取期權數據"}), 500
            
        return jsonify({"options_detail": df.to_dict(orient="records")})
    except Exception as e:
        app.logger.error(f"Error in get_options_detail: {str(e)}")
        return jsonify({"error": f"獲取數據時發生錯誤: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)