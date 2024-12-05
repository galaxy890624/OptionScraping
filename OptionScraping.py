import schedule
import time

# 下載資料套件
import requests as r

# 資料處理套件
import pandas as pd

url = "https://mis.taifex.com.tw/futures/api/getQuoteListOption"
payload = {"MarketType":"0",
           "SymbolType":"O",
           "KindID":"1",
           "CID":"TXO",
           "ExpireMonth":"202412W2", #格式 = 202406W4(for週選); 202407(for月選)
           "RowSize":"全部",
           "PageNo":"",
           "SortColumn":"",
           "AscDesc":"A"}
res = r.post(url, json = payload)
#print(res) # success = 200

'''
data
{'RtCode': '0', 'RtMsg': '', 'RtData': {'QuoteList': [{'SymbolID': 'TX420200K4-O', 'SpotID': '', 'DispCName': '臺指選W4114;20200買權', 'DispEName': 'TX4W4114;20200C', 'Status': 'TC', 'CBidPrice1': '2800.000', 'CBidSize1': '5', 'CAskPrice1': '2830.000', 'CAskSize1': '5', 'CTotalVolume': '', 'COpenPrice': '0.000', 'CHighPrice': '0.000', 'CLowPrice': '0.000', 'CLastPrice': '', 'CRefPrice': '2370.000', 'CCeilPrice': '4620.000', 'CFloorPrice': '115.000', 'CP': 'C', 'StrikePrice': '20200', 'SettlementPrice': '2810.000', 'OpenInterest': '0', 'CDate': '20241122', 'CTime': '', 'SpotWeights': '1.0', 'CTestTime': '', 'CBestBidPrice': '2800.000', 'CBestAskPrice': '2830.000', 'CBestBidSize': '5', 'CBestAskSize': '5'}, ...}
'''
data = res.json()
#print(data)

'''
把data做成表格
SymbolID SpotID         DispCName        DispEName Status CBidPrice1 CBidSize1 CAskPrice1 CAskSize1  ... OpenInterest     CDate   CTime SpotWeights CTestTime CBestBidPrice CBestAskPrice CBestBidSize CBestAskSize
'''
df = pd.DataFrame(data['RtData']['QuoteList'])
#print(df)

'''
DispCName CBidPrice1 CAskPrice1 CLastPrice CTotalVolume   CTime
如果這裡報錯, 可能的解決方案:
payload的結算時間ExpireMonth 過期了
'''
df = df[["DispCName", "CBidPrice1", "CAskPrice1", "CLastPrice", "CTotalVolume", "CTime"]]
#print(df)

'''
商品,到期月份,履約價,買賣權        買進        賣出    成交價  成交量      時間
[140 rows x 6 columns]
'''
df.columns = ['商品,到期月份,履約價,買賣權', '買進', '賣出', '成交價', '成交量', '時間']
#print(df)

'''
商品,到期月份,履約價,買賣權        買進        賣出    成交價  成交量      時間   商品,到期月份  履約價,買賣權
[140 rows x 8 columns]
'''
df[['商品,到期月份', '履約價,買賣權']] = df['商品,到期月份,履約價,買賣權'].str.split(';', expand=True) #用分號拆分
#print(df)

'''
商品,到期月份,履約價,買賣權        買進        賣出    成交價  成交量      時間   商品,到期月份  履約價,買賣權   商品   到期月份
[140 rows x 10 columns]
'''
df['商品'] = df['商品,到期月份'].str[:3]
df['到期月份'] = df['商品,到期月份'].str[3:]
#print(df)

'''
商品,到期月份,履約價,買賣權        買進        賣出    成交價  成交量      時間   商品,到期月份  履約價,買賣權   商品   到期月份    履約價 買賣權
[140 rows x 12 columns]
'''
df['履約價'] = df['履約價,買賣權'].str[:-2]
df['買賣權'] = df['履約價,買賣權'].str[-2:]
#print(df)

df = df[["商品", "到期月份", "買賣權", "履約價", "買進", "賣出", "成交價", "成交量", "時間"]]
print(df)

#print(df["成交價"])
#https://zh.wikipedia.org/zh-tw/%E5%B8%83%E8%8E%B1%E5%85%8B-%E8%88%92%E5%B0%94%E6%96%AF%E6%A8%A1%E5%9E%8B