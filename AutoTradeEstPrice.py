#Check Spot wallet and buy/sell coin with Binance
#Author: A.P
from __future__ import division
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException
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
    print("max value: "+str(max_value)+" min value: "+str(min_value)+" diff: "+ str(max_value/min_value)+ " avg value "+str(avg_value)+ " ")

    numMax = 0
    numMin = 0
    for x in hourPrice:
        if x >= max_value/1.003:
            numMax += 1
        elif x <= min_value*1.003:
            numMin += 1
    print("Num Max: "+str(numMax)+" Num Min: "+str(numMin))
    return hourPrice

def roundDown(pr, a):
    return float(math.floor(pr/a))*a 

hourPrice=resetDf()
max_value = max(hourPrice)
min_value = min(hourPrice)
avg_value = 0 if len(hourPrice) == 0 else sum(hourPrice)/len(hourPrice)

start_action = settings.action
action = start_action

volume = 0.0
amount = client.get_asset_balance(asset=coin)['free']
usdamount = client.get_asset_balance(settings.paircoin)['free']

roundLevel = 1.0
if min_value > 1000:
    roundLevel = 0.001
elif max_value < 1.0:
    roundLevel = 1.0
else:
    roundLevel = 0.01


def getVolume(action, amount, usdamount, min_value, max_value, roundLevel, usdset):
    volume = 0.0
    if usdset == 0:
        if float(amount)>0 and action == "SELL":
            volume = roundDown(float(amount),roundLevel)
        if float(usdamount)>0 and action == "BUY":
            volume = roundDown(float(usdamount)/(min_value*1.003),roundLevel)
    else:
        if float(amount)>0 and action == "SELL":
            volume = roundDown(float(usdamount)/(max_value/1.003),roundLevel)
            if volume > float(amount):
                volume = roundDown(float(amount),roundLevel)
        if float(usdamount)>0 and action == "BUY":
            if float(usdset) < float(usdamount):
                volume = roundDown(float(float(usdset)/(min_value*1.003)),roundLevel)
            else: 
                volume = roundDown(float(usdamount)/(min_value*1.003),roundLevel)
    return volume


volume = getVolume(action, amount, usdamount, min_value, max_value, roundLevel, settings.usd)

print("\nChecking...\n The amount of "+settings.paircoin+": "+str(usdamount)+" | The amount of "+coin+": "+str(amount)+"\nTry "+start_action+" "+coin+" with volume: "+str(volume))

if volume == 0.0:
    sys.exit("Invalid quantity (too small to trade)")

stop = 0

t = 0
selltry = 0
while stop == 0:
    prices = client.get_all_tickers()
    price = getPrice(coin, prices)
    if float(price) > float(max_value):
        print("Current price: "+price+" [ min ("+str(round(float(price)/min_value,3)- 1.0) +") -> max ("+str(round(max_value/float(price),3) - 1.0) + ") -> current ]")
    elif float(price) < float(min_value):
        print("Current price: "+price+" [ current -> min ("+str(round(float(price)/min_value,3)- 1.0) + ") -> max ("+str(round(max_value/float(price),3) - 1.0) + ") ]")
    else:
        print("Current price: "+price+" [ min ("+str(round(float(price)/min_value,3)- 1.0) + ") -> current -> max ("+str(round(max_value/float(price),3) - 1.0)+") ]" )

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
        volume = getVolume(action, amount, usdamount, min_value, max_value, roundLevel, settings.usd)
        print("Reset volume to trade: "+str(volume))
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
                    volume = getVolume(action, amount, usdamount, min_value, max_value, roundLevel, settings.usd)
                    print("Reset volume to trade: "+str(volume))
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
                        volume = getVolume(action, amount, usdamount, min_value, max_value, roundLevel, settings.usd)
                        print("Reset volume to trade: "+str(volume))
                   
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
                    volume = getVolume(action, amount, usdamount, min_value, max_value, roundLevel, settings.usd)
                    print("Reset volume to trade: "+str(volume))
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
                        volume = getVolume(action, amount, usdamount, min_value, max_value, roundLevel, settings.usd)
                        print("Reset volume to trade: "+str(volume))
        
    time.sleep(10)
    if volume == 0.0:
        stop = 1
    pamount = client.get_asset_balance(asset=coin)['free']
    usdn = client.get_asset_balance(settings.paircoin)['free']
    if float(usdn) < 10.0 and action == "BUY":
        stop = 1

    if float(pamount) < 10.0/float(price) and action == "SELL":
        stop = 1

    if float(pamount) >= float(amount)/1.001 and float(pamount) <= float(amount)*1.001 and float(usdn) > float(usdamount)+settings.limit:
        stop = 1

client.close_connection()   
