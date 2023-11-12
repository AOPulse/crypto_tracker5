from flask import Flask, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

def get_prices():
    coins = ["BTC", "ETH", "XRP", "DOGE", "ADA", "SOL", "LINK", "BNB", "CAKE", "ARB"]

    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD".format(",".join(coins))).json()["RAW"]

    data = {}
    for coin in crypto_data:
        data[coin] = {
            "coin": coin,
            "price": round(crypto_data[coin]["USD"]["PRICE"], 2),  # Rounded to 2 decimal places
            "change_day": round(crypto_data[coin]["USD"]["CHANGEPCT24HOUR"], 2),  # Rounded to 2 decimal places
            "change_hour": round(crypto_data[coin]["USD"]["CHANGEPCTHOUR"], 2),  # Rounded to 2 decimal places
        }

    return data

def get_historical_data(coin, days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    end_timestamp = int(end_date.timestamp())
    start_timestamp = int(start_date.timestamp())

    response = requests.get(
        f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={coin}&tsym=USD&limit={days}&toTs={end_timestamp}").json()

    labels = []
    data = []

    if response.get("Data") and response["Data"].get("Data"):
        historical_data = response["Data"]["Data"]
        for day_data in historical_data:
            date = datetime.utcfromtimestamp(day_data["time"]).strftime('%Y-%m-%d')
            labels.append(date)
            data.append(day_data["close"])

    return labels, data

@app.route('/')
def home():
    crypto_data = get_prices()
    chart_data = {}  # Create an empty dictionary to store chart data

    for coin in crypto_data:
        chart_labels, chart_prices = get_historical_data(coin)
        chart_data[coin] = {"labels": chart_labels, "data": chart_prices}

    return render_template('index.html', crypto_data=crypto_data, chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)
