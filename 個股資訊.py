import twstock as t
import pandas as p
import plotly.express as e


stock_code = input("請輸入股票代碼：")
stock = t.Stock(stock_code)
date = stock.date
price = stock.price
amount = stock.capacity



stock = t.realtime.get(stock_code)

result = p.DataFrame(stock).T.iloc[1:3]
result.columns = ['股票代碼','地區','股票名稱','公司全名','現在時間','最新成交價','成交量','累計成交量','最佳5檔賣出價','最佳5檔賣出量','最佳5檔買進價','最佳5檔買進量','開盤價','最高價','最低價']
result


data_price = p.DataFrame({'日期': date, '收盤價': price})
fig_price = e.line(data_price, x='日期', y='收盤價', title=f'{stock_code} 收盤價')
fig_price.show()


data_amount = p.DataFrame({'日期': date, '成交量': amount})
fig_amount = e.bar(data_amount, x='日期', y='成交量', title=f'{stock_code} 成交量')
fig_amount.show()
