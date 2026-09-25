import pandas as pd
import requests
import twstock
from bs4 import BeautifulSoup

YAHOO_URL = 'https://tw.stock.yahoo.com/quote/{}'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

REALTIME_COLUMNS = ['股票代碼', '地區', '股票名稱', '公司全名', '現在時間', '最新成交價', '成交量', '累計成交量',
                    '最佳5檔賣出價', '最佳5檔賣出量', '最佳5檔買進價', '最佳5檔買進量', '開盤價', '最高價', '最低價']
HISTORY_COLUMNS = ['日期', '成交股數', '成交量', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']


def to_float(text):
    try:
        return float(text.strip().replace(',', '').replace('+', '').replace('−', '-'))
    except (AttributeError, ValueError):
        return None


def get_stock_price(code):
    resp = requests.get(YAHOO_URL.format(code), headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    title = soup.find('h1')
    price = soup.select_one('.Fz\\(32px\\)')
    change = soup.select_one('.Fz\\(20px\\)')

    return (
        title.get_text(strip=True) if title else code,
        to_float(price.get_text()) if price else None,
        to_float(change.get_text()) if change else None,
    )


def get_realtime_table(code):
    data = twstock.realtime.get(code)
    if not data.get('success'):
        return None
    df = pd.DataFrame(data).T.iloc[1:3]
    df.columns = REALTIME_COLUMNS
    return df


def get_history(code, year=None, month=None):
    stock = twstock.Stock(code)
    if year and month:
        rows = stock.fetch(int(year), int(month))
    elif year:
        rows = stock.fetch_from(int(year), 1)
    else:
        rows = stock.fetch_31()

    df = pd.DataFrame(rows)
    if not df.empty:
        df.columns = HISTORY_COLUMNS
    return df
