# 套件匯入
import requests as r
import pandas as pd
from math import log, sqrt # log 是以e為底
from scipy.stats import norm

def get_spot_price_taifex():
    url = "https://mis.taifex.com.tw/futures/api/getQuoteList"
    payload = {"MarketType":"0",
           "SymbolType":"F",
           "KindID":"1",
           "CID":"TXF",
           "ExpireMonth":"",
           "RowSize":"全部",
           "PageNo":"",
           "SortColumn":"",
           "AscDesc":"A"}
    res = r.post(url, json=payload)
    '''
    以下是 data 的格式
    {'SymbolID': 'TXFL4-F', 'SpotID': '', 'DispCName': '臺指期124', 'DispEName': 'TX124', 'Status': '', 'CBidPrice1': '22183.00', 'CBidSize1': '10', 'CAskPrice1': '22185.00', 'CAskSize1': '4', 'CTotalVolume': '26918', 'COpenPrice': '22210.00', 'CHighPrice': '22221.00', 'CLowPrice': '22004.00', 'CLastPrice': '22185.00', 'CRefPrice': '22330.00', 'CCeilPrice': '24563.00', 'CFloorPrice': '20097.00', 'SettlementPrice': '', 'OpenInterest': '', 'CDate': '20241129', 'CTime': '092652', 'CTestTime': '084455', 'CDiff': '-145.00', 'CDiffRate': '-0.65', 'CAmpRate': '0.97', 'CBestBidPrice': '22183.00', 'CBestAskPrice': '22185.00', 'CBestBidSize': '10', 'CBestAskSize': '4', 'CTestPrice': '22216.00', 'CTestVolume': '201'}
    第1筆資料 = 加權指數(台指現貨)
    第2筆資料 = 近月
    第3筆資料 = 次月
    通常是用第2筆資料
    '''
    data = res.json()
    spot_price = float(data['RtData']['QuoteList'][1]['CLastPrice'])  # float(data['RtData']['QuoteList'][1]['CLastPrice']) = 取第2筆資料
    return spot_price
    #return data

spot_price = get_spot_price_taifex()
print(f"近月價格: {spot_price}")