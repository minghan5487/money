"""股票資料取得：Yahoo 奇摩股市即時報價爬蟲 + twstock 即時 / 歷史資料。"""
import pandas as pd
import requests
import twstock
from bs4 import BeautifulSoup

YAHOO_QUOTE_URL = 'https://tw.stock.yahoo.com/quote/{code}'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

REALTIME_COLUMNS = ['股票代碼', '地區', '股票名稱', '公司全名', '現在時間', '最新成交價', '成交量', '累計成交量',
                    '最佳5檔賣出價', '最佳5檔賣出量', '最佳5檔買進價', '最佳5檔買進量', '開盤價', '最高價', '最低價']
HISTORY_COLUMNS = ['日期', '成交股數', '成交量', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']


def _to_float(text):
    try:
        return float(text.strip().replace(',', '').replace('+', '').replace('−', '-'))
    except (AttributeError, ValueError):
        return None


def get_stock_price(stock_code):
    """從 Yahoo 奇摩股市取得 (股票名稱, 現價, 漲跌)。取不到的欄位回傳 None。"""
    resp = requests.get(YAHOO_QUOTE_URL.format(code=stock_code), headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    title_el = soup.find('h1')
    price_el = soup.select_one('.Fz\\(32px\\)')
    change_el = soup.select_one('.Fz\\(20px\\)')

    title = title_el.get_text(strip=True) if title_el else stock_code
    current_price = _to_float(price_el.get_text()) if price_el else None
    change = _to_float(change_el.get_text()) if change_el else None
    return title, current_price, change


def get_realtime_table(stock_code):
    """twstock 即時資訊，整理成單列 DataFrame。"""
    data = twstock.realtime.get(stock_code)
    if not data.get('success'):
        return None
    df = pd.DataFrame(data).T.iloc[1:3]
    df.columns = REALTIME_COLUMNS
    return df


def get_history(stock_code, year=None, month=None):
    """歷史日成交資料：指定年月 → 該月；只指定年 → 該年 1 月至今；皆未指定 → 最近 31 個交易日。"""
    stock = twstock.Stock(stock_code)
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
