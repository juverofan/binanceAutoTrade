#Check Spot wallet and buy/sell coin with Binance
#Author: A.P
from __future__ import division
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import os
import time
import sys
import argparse
import math

def getPrice(coin, pr):
    pr1 = 0.0
    for price in pr:
        if coin+"BUSD" == price['symbol']:
            pr1 = float(price['price'])
            return price['price']
        elif coin.startswith("LD") and coin.endswith("2"):
            coin = coin[2:len(coin)-1]
            if coin+"BUSD" == price['symbol']:
                pr1 = float(price['price'])
                return price['price']
    if pr1 == 0.0:
        return pr1



print("===============SCRIPT TO FIND THE UNSTABLE COIN FROM BINANCE=================\nAuthor: A.P\nWebsite: https://topvl.net\nBitcoin Address: 1Dbu7Hwrmd2iT6xSxKf4rYrYiufukQLAjt")
print("===================================================================")

api_key = ''
api_secret = ''
client = Client(api_key, api_secret)


hourPrice = []
min_value = 0.0
max_value = 0.0
avg_value = 0.0

prices = client.get_all_tickers()

for pr in prices:
    if pr['symbol'].endswith('BUSD') and 'BULL' not in pr['symbol'] and 'BEAR' not in pr['symbol']:
    
        avgPrice =  client.get_avg_price(symbol = pr['symbol'])['price']
        #print(avgPrice)
        #t = 0
        hourPrice = []
        for kline in client.get_historical_klines(pr['symbol'], Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC"):
            hourPrice.append(float(kline[1]))
        #print(hourPrice)
        coin = pr['symbol'][0:len(pr['symbol'])-4]
        if len(hourPrice) > 50:
            max_value = max(hourPrice)
            min_value = min(hourPrice)
            avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
            if max_value/min_value > 1.03:
                strOut = "======================"+coin+"========================\n"
                strOut += "[sta - "+str(hourPrice[0])+" - end: "+str(hourPrice[len(hourPrice)-1])+"]\n[max: "+str(max_value)+" - min: "+str(min_value)+"]\n[diff: "+ str(max_value/min_value)+ "]\n[avg: "+str(avg_value)+ " avgPrice: "+str(avgPrice)+"]"

                numMax = 0
                numMin = 0
                for x in hourPrice:
                    if x >= max_value/1.003:
                        numMax += 1
                    elif x <= min_value*1.003:
                        numMin += 1
                strOut += "\n[Num Max: "+str(numMax)+" Num Min: "+str(numMin)+"]"
                if numMax + numMin >= 10 and numMax >= 3 and numMin >= 3:
                    strOut += "\n(***) ======================> "+coin+"<================ (***)\n"
                elif numMax >= 3 and numMin >= 3:
                    strOut += "\n(*) ======> "+coin+" <====== (*)\n"
                print(strOut)
    
client.close_connection()   
