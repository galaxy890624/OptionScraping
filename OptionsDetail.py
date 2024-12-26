import requests
url = "https://openapi.taifex.com.tw/v1/OptionsTimeAndSalesData" # 每一筆的成交明細
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(data) # 這裡可以處理數據，繪製 K 線圖等
else:
    print(f"Error: {response.status_code}")