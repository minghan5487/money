import plotly.express as px

from stock_service import get_history

if __name__ == '__main__':
    code = input('請輸入股票代碼：').strip()
    year = input('年份（留空 = 最近 31 個交易日）：').strip() or None
    month = input('月份（留空 = 整年）：').strip() or None

    history = get_history(code, year, month)
    print(history)

    if not history.empty:
        px.line(history, x='日期', y='收盤價', title=f'{code} 收盤價').show()
        px.bar(history, x='日期', y='成交量(張)',title=f'{code} 成交量').show()
