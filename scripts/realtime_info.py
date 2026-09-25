import plotly.express as px

from stock_service import get_history, get_realtime

if __name__ == '__main__':
    code = input('請輸入股票代碼：').strip()

    summary, order_book = get_realtime(code)
    if summary is None:
        print('無法取得即時資訊')
    else:
        print(summary.T.to_string(header=False))
        print(order_book.to_string(index=False))

    history = get_history(code)
    px.line(history, x='日期', y='收盤價', title=f'{code} 收盤價').show()
    px.bar(history, x='日期', y='成交量(張)', title=f'{code} 成交量').show()
