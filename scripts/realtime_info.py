import plotly.express as px

from stock_service import get_history, get_realtime_table

if __name__ == '__main__':
    code = input('請輸入股票代碼：').strip()

    realtime = get_realtime_table(code)
    print('無法取得即時資訊' if realtime is None else realtime.T)

    history = get_history(code)
    px.line(history, x='日期', y='收盤價', title=f'{code} 收盤價').show()
    px.bar(history, x='日期', y='成交量', title=f'{code} 成交量').show()
