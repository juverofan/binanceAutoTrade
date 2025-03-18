# binanceAutoTrade
Some PYTHON scripts to help trading automatically on Binance<br>

Requirements:<br>
- Python 3.9<br>
- python-binance lib (<i><b>command:</b> pip install python-binance</i>) or (<b>pip install -r requirements.txt</b>)
- Binance API setup<br>

<br>
<b>SETUP GUIDE</b><br>
<b>Step 1: </b> Install Python 3.9<br>
<b>Step 2: </b> Install Binance API (Go to API Management, create and save API key and API secret key, then paste into viewUnstableCoin.py and settings.py)<br>
<b>Step 3: </b> Install python-binance (use Command line: pip install python-binance)<br>
<br><br>
<b>Scripts:<br>
 viewUnstableCoin.py</b>: find the unstable coin in an hour (the price is unstable)<br>
 <b>Command:</b> python viewUnstableCoin.py<br>
 <br>
 <b>AutoTradeEstPrice.py</b>: auto trading with the estimate price (recommend the unstable coin, BUY when reach the minimum price and SELL when reach the maximum price)<br>
 <b>Command:</b> python AutoTradeEstPrice.py<br>
 
 <b>settings.py</b>: setting file for AutoTradeEstPrice.py, with parameters:<br>
 - API key, API secret: binance API key, secret key
 - coin: coin you want to trade
 - paircoin: the pair coin (BUSD or USDT)
 - action: the start action (SELL or BUY)
 - usd: the volume of paircoin (USD) you want to trade, if set this value equals 0, the volume equals the amount of coin (pair coin) you have.
 - limit: the value (USD) you want to stop trading 

<br><br>
<b><font color='red'>Warning: </font></b>You can lose your money, if the prices changes too much.
