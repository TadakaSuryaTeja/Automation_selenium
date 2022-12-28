import csv
import time

import requests

stock_name_list = ["ADANIPORTS", "ASIANPAINT", "RELIANCE", "ADANIPOWER", "AXISBANK", "CIPLA", "BAJAJ-AUTO",
                   "BAJFINANCE", "BPCL", "BHARTIARTL", "CIPLA", "COALINDIA", "EICHERMOT", "GAIL", "HCLTECH", "HDFCBANK",
                   "INFY", "ICICIBANK", "LUPIN", "NTPC", "HEROMOTOCO", "BHARATRAS", "BIRLACORPN", "DRREDDY", "GRASIM",
                   "HDFC", "ITC", "IBULHSGFIN", "IOC", "INDUSINDBK", "KOTAKBANK", "LT", "M&M", "MARUTI", "NTPC", "ONGC",
                   "POWERGRID", "SBIN", "SUNPHARMA", "TCS", "TATAMOTORS", "TATASTEEL", "TECHM", "ULTRACEMCO",
                   "UNIONBANK", "MCDOWELL-N", "VEDL", "WIPRO", "ZEEL", "NESTLEIND"
                   ]


def fetch_and_save_csv(stock_name):
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock_name}.BSE&outputsize' \
              f'=full&apikey='

        r = requests.get(url)
        data = r.json()

        keys = ['Date', 'Stock Name', '1. open', '2. high', '3. low', '4. close', '5. adjusted close', '6. volume',
                '7. dividend amount', '8. split coefficient']

        with open(f'{stock_name}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(keys)
            for inner_keys, values in data['Time Series (Daily)'].items():
                values['Date'] = inner_keys
                values['Stock Name'] = stock_name
                row = [values[key] for key in keys]
                writer.writerow(row)
            f.close()
    except Exception as ex:
        print(f"Failed {stock_name}", ex)


count = 0
for stock_name in stock_name_list:
    if count % 5 == 0:
        time.sleep(60)
    count += 1
    fetch_and_save_csv(stock_name)
