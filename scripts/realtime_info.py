import plotly.express as px

import twse_api
from stock_service import get_history, get_realtime

if __name__ == '__main__':
    code = input('請輸入股票代碼：').strip()

    quote = twse_api.get_quote(code)
    if quote:
        print(f"{quote['name']} {quote['date']} 收盤 {quote['close']}（{quote['change']:+}）")

    realtime = get_realtime(code)
    if realtime:
        print(f"即時成交價 {realtime['price']}（{realtime['time']}）")
        for row in realtime['order_book']:
            print(f"{row['bid_volume']:>6} {str(row['bid']):>10} | {str(row['ask']):<10} {row['ask_volume']}")

    history = get_history(code)
    px.line(history, x='日期', y='收盤價', title=f'{code} 收盤價').show()
    px.bar(history, x='日期', y='成交量(張)', title=f'{code} 成交量').show()
