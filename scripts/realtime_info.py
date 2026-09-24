"""CLI：查詢個股即時資訊，並顯示最近 31 個交易日的收盤價與成交量圖。"""
import os
import sys

import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stock_service import get_history, get_realtime_table  # noqa: E402

if __name__ == '__main__':
    stock_code = input('請輸入股票代碼：').strip()

    realtime = get_realtime_table(stock_code)
    print(realtime.T if realtime is not None else '無法取得即時資訊')

    history = get_history(stock_code)
    px.line(history, x='日期', y='收盤價', title=f'{stock_code} 收盤價').show()
    px.bar(history, x='日期', y='成交量', title=f'{stock_code} 成交量').show()
