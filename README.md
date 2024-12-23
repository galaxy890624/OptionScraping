# OptionScraping
 
Web: http://127.0.0.1:5000/

Data: http://127.0.0.1:5000/api/options

# How to work
1. Run "..\App.py"
2. http://127.0.0.1:5000/
3. Press "刷新資料" button

# To do list
1. 無風險利率

# 關於 : 資料來源
1. 每一檔的選擇權數據

Step 1. https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/Options/
Step 2. F12 > Network > Fetch/XHR
如果 Name 沒有出現 getQuoteListOption 就刷新
step 3. 滑鼠放在 getQuoteListOption 上面 查看url 複製到python
step 4. Payload 或 Response

格式: {'RtCode': '0', 'RtMsg': '', 'RtData': {'QuoteList': [{'SymbolID': 'TX420200K4-O', 'SpotID': '', 'DispCName': '臺指選W4114;20200買權', 'DispEName': 'TX4W4114;20200C', 'Status': 'TC', 'CBidPrice1': '2800.000', 'CBidSize1': '5', 'CAskPrice1': '2830.000', 'CAskSize1': '5', 'CTotalVolume': '', 'COpenPrice': '0.000', 'CHighPrice': '0.000', 'CLowPrice': '0.000', 'CLastPrice': '', 'CRefPrice': '2370.000', 'CCeilPrice': '4620.000', 'CFloorPrice': '115.000', 'CP': 'C', 'StrikePrice': '20200', 'SettlementPrice': '2810.000', 'OpenInterest': '0', 'CDate': '20241122', 'CTime': '', 'SpotWeights': '1.0', 'CTestTime': '', 'CBestBidPrice': '2800.000', 'CBestAskPrice': '2830.000', 'CBestBidSize': '5', 'CBestAskSize': '5'}, ...}

2. 台指期

Step.1 https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/FuturesDomestic/
Step 2. F12 > Network > Fetch/XHR > Payload 或 Response
如果 Name 沒有出現 getQuoteList 就刷新
step 3. 滑鼠放在 getQuoteList 上面 查看url 複製到python
step 4. Payload 或 Response