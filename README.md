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

    以下是data的格式

        {'RtCode': '0', 'RtMsg': '', 'RtData': {'QuoteList': [{'SymbolID': 'TX420200K4-O', 'SpotID': '', 'DispCName': '臺指選W4114;20200買權', 'DispEName': 'TX4W4114;20200C', 'Status': 'TC', 'CBidPrice1': '2800.000', 'CBidSize1': '5', 'CAskPrice1': '2830.000', 'CAskSize1': '5', 'CTotalVolume': '', 'COpenPrice': '0.000', 'CHighPrice': '0.000', 'CLowPrice': '0.000', 'CLastPrice': '', 'CRefPrice': '2370.000', 'CCeilPrice': '4620.000', 'CFloorPrice': '115.000', 'CP': 'C', 'StrikePrice': '20200', 'SettlementPrice': '2810.000', 'OpenInterest': '0', 'CDate': '20241122', 'CTime': '', 'SpotWeights': '1.0', 'CTestTime': '', 'CBestBidPrice': '2800.000', 'CBestAskPrice': '2830.000', 'CBestBidSize': '5', 'CBestAskSize': '5'}, ...}

2. 台指期

    Step.1 https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/FuturesDomestic/

    Step 2. F12 > Network > Fetch/XHR > Payload 或 Response

    如果 Name 沒有出現 getQuoteList 就刷新

    step 3. 滑鼠放在 getQuoteList 上面 查看url 複製到python

    step 4. Payload 或 Response

    以下是 data 的格式

        {'SymbolID': 'TXFL4-F', 'SpotID': '', 'DispCName': '臺指期124', 'DispEName': 'TX124', 'Status': '', 'CBidPrice1': '22183.00', 'CBidSize1': '10', 'CAskPrice1': '22185.00', 'CAskSize1': '4', 'CTotalVolume': '26918', 'COpenPrice': '22210.00', 'CHighPrice': '22221.00', 'CLowPrice': '22004.00', 'CLastPrice': '22185.00', 'CRefPrice': '22330.00', 'CCeilPrice': '24563.00', 'CFloorPrice': '20097.00', 'SettlementPrice': '', 'OpenInterest': '', 'CDate': '20241129', 'CTime': '092652', 'CTestTime': '084455', 'CDiff': '-145.00', 'CDiffRate': '-0.65', 'CAmpRate': '0.97', 'CBestBidPrice': '22183.00', 'CBestAskPrice': '22185.00', 'CBestBidSize': '10', 'CBestAskSize': '4', 'CTestPrice': '22216.00', 'CTestVolume': '201'}

    第1筆資料 = 加權指數(台指現貨)

    第2筆資料 = 近月

    第3筆資料 = 次月

    通常是用第2筆資料