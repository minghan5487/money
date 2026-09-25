import pandas as pd
import twstock

HISTORY_COLUMNS = {
    'date': '日期', 'capacity': '成交股數', 'turnover': '成交金額', 'open': '開盤價', 'high': '最高價',
    'low': '最低價', 'close': '收盤價', 'change': '漲跌價差', 'transaction': '成交筆數',
}


def to_float(text):
    try:
        return float(str(text).replace(',', ''))
    except ValueError:
        return None


def is_valid_code(code):
    return code in twstock.codes


def get_name(code):
    info = twstock.codes.get(code)
    return info.name if info else code


def get_realtime(code):
    data = twstock.realtime.get(code)
    if not data.get('success'):
        return None

    rt = data['realtime']
    return {
        'time': data['info']['time'],
        'price': to_float(rt['latest_trade_price']),
        'volume': rt['accumulate_trade_volume'],
        'order_book': [
            {'bid_volume': bv, 'bid': to_float(bp), 'ask': to_float(ap), 'ask_volume': av}
            for bp, bv, ap, av in zip(rt['best_bid_price'], rt['best_bid_volume'],
                                      rt['best_ask_price'], rt['best_ask_volume'])
        ],
    }


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
