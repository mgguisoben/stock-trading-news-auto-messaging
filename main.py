import datetime as dt
import os

import requests
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
ACCT_SID = os.environ.get("ACCT_SID")
DEMO_PHONE = os.environ.get("DEMO_PHONE")
MY_PHONE = os.environ.get("MY_PHONE")

# Get today's and yesterday's date
# note: Adjusted to 2 days back
today = dt.datetime.now().date() - dt.timedelta(2)
yday = today - dt.timedelta(1)
today, yday = str(today), str(yday)  # Convert datetime objects to str

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

# Get TSLA stock price for today and yesterday from alphavantage
stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_price = stock_response.json()["Time Series (Daily)"]
stock_price_today = float(stock_price[today]["1. open"])
stock_price_yday = float(stock_price[yday]["4. close"])
# Get percent difference of today's and yesterday's stock price
stock_price_delta = (stock_price_today - stock_price_yday) / stock_price_yday * 100

news_params = {
    'q': 'TSLA',
    'apiKey': NEWS_API_KEY,
    'from': yday,
    'to': today,
    'language': 'en',
    'sortBy': 'relevancy'
}

# Get news from NEWS API
news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()

news = news_response.json()['articles']

# Send news to phone through Twilio
client = Client(ACCT_SID, AUTH_TOKEN)

# Check if stock increased/decreased by 5%
if abs(stock_price_delta) < 5:
    if stock_price_delta > 0:
        symbol = "🔺"
    else:
        symbol = "🔻"

    for i in range(3):
        content = (f"{COMPANY_NAME}: {symbol}{int(stock_price_delta)}\n"
                   f"Headline: {news[i]['title']}\n"
                   f"Brief: {news[i]['content']}\n")
        print(content)

        message = client.messages.create(
            from_=DEMO_PHONE,
            body=content,
            to=MY_PHONE
        )

        print(message.sid)  # Check if message went through
