import csv
import time

import requests
from tqdm import tqdm

stock_name_list = ["HDFCBANK", "ICICIBANK",
                   "SBIN",
                   "KOTAKBANK",
                   "AXISBANK",
                   "YESBANK",
                   "INDUSINDBK",
                   "FEDERALBNK",
                   "BANKBARODA",
                   "PNB",
                   "BANKINDIA",
                   "CANBK"]
api_key = ""


def fetch_and_save_csv(stock_name):
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock_name}.BSE&outputsize' \
              f'=full&apikey={api_key}'

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
for stock_name in tqdm(stock_name_list):
    if count % 5 == 0:
        time.sleep(60)
    count += 1
    fetch_and_save_csv(stock_name)
