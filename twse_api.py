import time
from datetime import date

import requests

BASE_URL = 'https://openapi.twse.com.tw/v1'
CACHE_SECONDS = 600

_cache = {}


def fetch(endpoint):
    cached = _cache.get(endpoint)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]

    resp = requests.get(f'{BASE_URL}{endpoint}', timeout=30)
    resp.raise_for_status()
    data = resp.json()
    _cache[endpoint] = (time.time(), data)
    return data


def num(value):
    try:
        return float(str(value).replace(',', ''))
    except ValueError:
        return None


def roc_date(value):
    value = str(value)
    if len(value) == 8:
        return date(int(value[:4]), int(value[4:6]), int(value[6:]))
    return date(int(value[:-4]) + 1911, int(value[-4:-2]), int(value[-2:]))


def find_by_code(endpoint, code):
    return next((row for row in fetch(endpoint) if row['Code'] == code), None)


def get_quote(code):
    row = find_by_code('/exchangeReport/STOCK_DAY_ALL', code)
    if not row:
        return None

    close, change = num(row['ClosingPrice']), num(row['Change'])
    prev_close = close - change if close is not None and change is not None else None
    return {
        'name': row['Name'],
        'date': roc_date(row['Date']),
        'open': num(row['OpeningPrice']),
        'high': num(row['HighestPrice']),
        'low': num(row['LowestPrice']),
        'close': close,
        'change': change,
        'change_pct': change / prev_close * 100 if prev_close else None,
        'volume': int(num(row['TradeVolume']) // 1000),
        'value': num(row['TradeValue']),
        'transactions': int(num(row['Transaction'])),
    }


def get_valuation(code):
    row = find_by_code('/exchangeReport/BWIBBU_ALL', code)
    if not row:
        return None
    return {'pe': num(row['PEratio']), 'dividend_yield': num(row['DividendYield']), 'pb': num(row['PBratio'])}


def get_taiex():
    row = fetch('/exchangeReport/FMTQIK')[-1]
    index, change = num(row['TAIEX']), num(row['Change'])
    return {
        'date': roc_date(row['Date']),
        'index': index,
        'change': change,
        'change_pct': change / (index - change) * 100,
        'value': num(row['TradeValue']),
    }


def get_top_volume(limit=10):
    rows = []
    for row in fetch('/exchangeReport/MI_INDEX20')[:limit]:
        change = num(row['Change'])
        if row['Dir'].strip() == '-':
            change = -change
        rows.append({
            'code': row['Code'],
            'name': row['Name'],
            'close': num(row['ClosingPrice']),
            'change': change,
            'volume': int(num(row['TradeVolume']) // 1000),
        })
    return rows
