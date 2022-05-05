#Check Spot wallet and buy/sell coin with Binance
#Author: A.P
from __future__ import division
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import os
import time
import sys
import argparse
import math
import settings

def getPrice(coin, pr):
    pr1 = 0.0
    for price in pr:
        if coin+settings.paircoin == price['symbol']:
            pr1 = float(price['price'])
            return price['price']
        elif coin.startswith("LD") and coin.endswith("2"):
            coin = coin[2:len(coin)-1]
            if coin+settings.paircoin == price['symbol']:
                pr1 = float(price['price'])
                return price['price']
    if pr1 == 0.0:
        return pr1


print("===============SCRIPT FOR AUTOTRADING FROM BINANCE=================\nAuthor: A.P\nWebsite: https://topvl.net\nBitcoin Address: 1Dbu7Hwrmd2iT6xSxKf4rYrYiufukQLAjt")
print("===================================================================")

api_key = settings.api_key
api_secret = settings.api_secret
client = Client(api_key, api_secret)

coin = "NEAR"
coin = settings.coin.upper()


hourPrice = []
min_value = 0.0
max_value = 0.0
avg_value = 0.0
def resetDf():
    #prices = client.get_all_tickers()

    avgPrice =  client.get_avg_price(symbol = coin+settings.paircoin)['price']
    #print(avgPrice)
    #t = 0
    hourPrice = []
    for kline in client.get_historical_klines(coin+settings.paircoin, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC"):
        hourPrice.append(float(kline[1]))
    print("----THE PRICE OF THE LASTEST HOUR--------")
    print(hourPrice)

    max_value = max(hourPrice)
    min_value = min(hourPrice)
    avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
    print("max: "+str(max_value)+" min: "+str(min_value)+" diff: "+ str(max_value/min_value)+ " avg: "+str(avg_value)+ " avgPrice: "+str(avgPrice))

    numMax = 0
    numMin = 0
    for x in hourPrice:
        if x >= max_value/1.003:
            numMax += 1
        elif x <= min_value*1.003:
            numMin += 1
    print("Num Max: "+str(numMax)+" Num Min: "+str(numMin))
    return hourPrice

hourPrice=resetDf()
max_value = max(hourPrice)
min_value = min(hourPrice)
avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)

start_action = settings.action
action = start_action

volume = 0.0
amount = client.get_asset_balance(asset=coin)['free']
usdamount = client.get_asset_balance(settings.paircoin)['free']
if settings.usd == 0:
    if float(amount)>0 and action == "SELL":
        volume = math.floor(float(amount))
    if float(usdamount)>0 and action == "BUY":
        volume = math.floor(float(usdamount)/(min_value*1.003))
else:
    if float(amount)>0 and action == "SELL":
        volume = math.floor(float(usdamount)/(max_value/1.003))
        if volume > float(amount):
            volume = math.floor(float(amount))
    if float(usdamount)>0 and action == "BUY":
        if float(settings.usd) < float(usdamount):
            volume = math.floor(float(float(settings.usd)/(min_value*1.003)))
        else: 
            volume = math.floor(float(usdamount)/(min_value*1.003))
stop = 0

t = 0
selltry = 0
while stop == 0:
    prices = client.get_all_tickers()
    price = getPrice(coin, prices)
    print(price+" max: "+str(max_value/float(price)) + " - min: "+str(float(price)/min_value))

    if action == "SELL" and start_action == "SELL":
        selltry += 1

    if action == "BUY" and start_action == "BUY":
        selltry += 1

    if selltry == 50:
        #if start_action == "SELL":
        hourPrice=resetDf()
        max_value = max(hourPrice)
        min_value = min(hourPrice)
        avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
        selltry = 1

    if action == "BUY" and start_action == "SELL":
        selltry = 0

    if action == "SELL" and start_action == "BUY":
        selltry = 0

    if action == "SELL" and float(price) >= max_value/1.003:
        t += 1 
        if float(price) >= max_value/1.001 or t >= 5:
            order = client.order_limit_sell(
                        symbol=coin+settings.paircoin,
                        quantity=volume,
                        price=price)
            print("Trade info: "+str(order))
            time.sleep(2)
            if(order['status']=='FILLED'):
                action = "BUY"
                fills = order['fills']
                #print(str(fills))
                fillAmount = order['fills'][0]['qty']
                fillPrice = order['fills'][0]['price']
                currPrice = fillPrice
                fillSide = order['side']
                t = 0
                print("Action: "+str(fillSide)+" - amount: "+str(fillAmount)+" - price: "+str(fillPrice))
                if start_action == "BUY":
                    hourPrice=resetDf()
                    max_value = max(hourPrice)
                    min_value = min(hourPrice)
                    avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
            else:
                try:
                    client.cancel_order(symbol=coin+settings.paircoin,orderId=order['orderId'])
                    print("Transaction's cancelled.")
                except BinanceAPIException as e:
                    print(str(e.status_code)+str(e.message))
                    action = "BUY"
                    t = 0
                    if start_action == "BUY":
                        hourPrice=resetDf()
                        max_value = max(hourPrice)
                        min_value = min(hourPrice)
                        avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
                   
    if action == "BUY" and float(price) <= min_value*1.003:
        selltry = 0
        t += 1
        if float(price) <= min_value*1.001 or t > 5:
            order = client.order_limit_buy(
                        symbol=coin+settings.paircoin,
                        quantity=volume,
                        price=price)
            print("Trade info: "+str(order))
            time.sleep(2)
            if(order['status']=='FILLED'):
                action = "SELL"
                fills = order['fills']
                fillAmount = order['fills'][0]['qty']
                fillPrice = order['fills'][0]['price']
                currPrice = fillPrice
                fillSide = order['side']
                print("Action: "+str(fillSide)+" - amount: "+str(fillAmount)+" - price: "+str(fillPrice))
                t = 0
                if start_action == "SELL":
                    hourPrice=resetDf()
                    max_value = max(hourPrice)
                    min_value = min(hourPrice)
                    avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
            else:
                try:
                    client.cancel_order(symbol=coin+settings.paircoin,orderId=order['orderId'])
                    print("Transaction's cancelled.")
                except BinanceAPIException as e:
                    print(str(e.status_code)+str(e.message))
                    action = "SELL"
                    t = 0
                    if start_action == "SELL":
                        hourPrice=resetDf()
                        max_value = max(hourPrice)
                        min_value = min(hourPrice)
                        avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)
        
    time.sleep(10)
    pamount = client.get_asset_balance(asset=coin)['free']
    usdn = client.get_asset_balance(settings.paircoin)['free']
    if float(pamount) >= float(amount)/1.001 and float(pamount) <= float(amount)*1.001 and float(usdn) > float(usdamount)+settings.limit:
        stop = 1

client.close_connection()   
