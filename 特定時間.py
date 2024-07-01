import twstock as t
import pandas as p
import plotly.express as e

# 自定義輸入股票代碼
stock_code = input("請輸入股票代碼：")
stock = t.Stock(stock_code)

#製作最近一個月的資料
period = stock.fetch_31()
data = p.DataFrame(period)
data.columns = ['日期','成交股數','成交量','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
data

#製作2024年1月的資料
period = stock.fetch(2024,1)
data = p.DataFrame(period)
data.columns = ['日期','成交股數','成交量','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
data

#製作2024年1月到現在的資料
period = stock.fetch_from(2024,1)
data = p.DataFrame(period)
data.columns = ['日期','成交股數','成交量','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
#折線圖
fig_price = e.line(data, x='日期', y='收盤價', title=f'{stock_code} 收盤價')
fig_price.show()
#長條圖
fig_amount = e.bar(data, x='日期', y='成交量', title=f'{stock_code} 成交量')
fig_amount.show()