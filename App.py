from flask import Flask, jsonify, render_template
from Delta import main

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("Index.html")  # 前端頁面

@app.route('/api/deltas', methods=['GET'])
def get_deltas():
    data = main()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)