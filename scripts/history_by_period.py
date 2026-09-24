"""CLI：查詢指定期間的歷史成交資料並繪圖。年份、月份留空則為最近 31 個交易日。"""
import os
import sys

import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stock_service import get_history  # noqa: E402

if __name__ == '__main__':
    stock_code = input('請輸入股票代碼：').strip()
    year = input('年份（留空 = 最近 31 個交易日）：').strip() or None
    month = input('月份（留空 = 該年 1 月至今）：').strip() or None

    history = get_history(stock_code, year, month)
    print(history)
    if not history.empty:
        px.line(history, x='日期', y='收盤價', title=f'{stock_code} 收盤價').show()
        px.bar(history, x='日期', y='成交量', title=f'{stock_code} 成交量').show()
