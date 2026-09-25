import pandas as pd
import requests
import twstock
from bs4 import BeautifulSoup

YAHOO_URL = 'https://tw.stock.yahoo.com/quote/{}'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

HISTORY_COLUMNS = {
    'date': '日期', 'capacity': '成交股數', 'turnover': '成交金額', 'open': '開盤價', 'high': '最高價',
    'low': '最低價', 'close': '收盤價', 'change': '漲跌價差', 'transaction': '成交筆數',
}


def to_float(text):
    try:
        return float(text.strip().replace(',', '').replace('+', '').replace('−', '-'))
    except (AttributeError, ValueError):
        return None


def get_stock_price(code):
    resp = requests.get(YAHOO_URL.format(code), headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    titles = soup.find_all('h1')
    price = soup.select_one('.Fz\\(32px\\)')
    change_el = soup.select_one('.Fz\\(20px\\)')

    change = to_float(change_el.get_text()) if change_el else None
    if change and 'C($c-trend-down)' in change_el.get('class', []):
        change = -change

    return (
        titles[-1].get_text(strip=True) if titles else code,
        to_float(price.get_text()) if price else None,
        change,
    )


def is_valid_code(code):
    return code in twstock.codes


def get_realtime(code):
    data = twstock.realtime.get(code)
    if not data.get('success'):
        return None, None

    info, rt = data['info'], data['realtime']
    summary = pd.DataFrame([{
        '股票名稱': info['name'],
        '時間': info['time'],
        '成交價': to_float(rt['latest_trade_price']),
        '開盤價': to_float(rt['open']),
        '最高價': to_float(rt['high']),
        '最低價': to_float(rt['low']),
        '單量(張)': rt['trade_volume'],
        '累計成交量(張)': rt['accumulate_trade_volume'],
    }])
    order_book = pd.DataFrame({
        '買進價': map(to_float, rt['best_bid_price']),
        '買進量': rt['best_bid_volume'],
        '賣出價': map(to_float, rt['best_ask_price']),
        '賣出量': rt['best_ask_volume'],
    })
    return summary, order_book


def get_history(code, year=None, month=None):
    stock = twstock.Stock(code)
    if year and month:
        rows = stock.fetch(int(year), int(month))
    elif year:
        rows = stock.fetch_from(int(year), 1)
    else:
        rows = stock.fetch_31()

    df = pd.DataFrame([r._asdict() for r in rows], columns=list(HISTORY_COLUMNS))
    df = df.rename(columns=HISTORY_COLUMNS)
    df['成交量(張)'] = df['成交股數'] // 1000
    return df
