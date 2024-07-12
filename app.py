from flask import Flask, render_template, request, redirect, url_for
import twstock as t
import pandas as pd
import plotly.express as e
import plotly.io as pi
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BUY_PRICE = None
SELL_PRICE = None
records = []

def get_stock_price(stock_code):
    url = f'https://tw.stock.yahoo.com/quote/{stock_code}'
    web = requests.get(url)
    soup = BeautifulSoup(web.text, "html.parser")

    title = soup.find('h1').get_text()
    price_element = soup.select_one('.Fz\\(32px\\)')
    status_element = soup.select_one('.Fz\\(20px\\)')

    if price_element:
        current_price_text = price_element.get_text().strip().replace(',', '')
        try:
            current_price = float(current_price_text)
        except ValueError:
            current_price = None
    else:
        current_price = None

    if status_element:
        status = status_element.get_text().strip()
        try:
            change = float(status.replace('+', '').replace('−', '-').replace(',', ''))
        except ValueError:
            change = 0
    else:
        status = "無法找到狀態"
        change = 0

    return title, current_price, change

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock', methods=['POST'])
def stock():
    stock_code = request.form['stock_code']
    year = request.form.get('year')
    month = request.form.get('month')
    title, current_price, change = get_stock_price(stock_code)
    stock_realtime = t.realtime.get(stock_code)
    result = pd.DataFrame(stock_realtime).T.iloc[1:3]
    result.columns = ['股票代碼', '地區', '股票名稱', '公司全名', '現在時間', '最新成交價', '成交量', '累計成交量', 
                      '最佳5檔賣出價', '最佳5檔賣出量', '最佳5檔買進價', '最佳5檔買進量', '開盤價', '最高價', '最低價']
    stock = t.Stock(stock_code)
    if year and month:
        period = stock.fetch(int(year), int(month))
    elif year:
        period = stock.fetch_from(int(year), 1)
    else:
        period = stock.fetch_31()
    
    data = pd.DataFrame(period)
    data.columns = ['日期','成交股數','成交量','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
    fig_price = e.line(data, x='日期', y='收盤價', title=f'{stock_code} 收盤價')
    price_plot = pi.to_html(fig_price, full_html=False)
    fig_amount = e.bar(data, x='日期', y='成交量', title=f'{stock_code} 成交量')
    amount_plot = pi.to_html(fig_amount, full_html=False)

    return render_template('stock.html', stock_code=stock_code, result=result.to_html(classes='table table-bordered table-striped text-center'), 
                           title=title, current_price=current_price, change=change, 
                           price_plot=price_plot, amount_plot=amount_plot)

@app.route('/trading_zone', methods=['POST', 'GET'])
def trading_zone():
    global BUY_PRICE, SELL_PRICE, records

    if request.method == 'POST':
        stock_code = request.form['stock_code']
        current_price = float(request.form['current_price'])
        try:
            BUY_PRICE = float(request.form['buy_price']) if request.form['buy_price'] else None
            SELL_PRICE = float(request.form['sell_price']) if request.form['sell_price'] else None
        except ValueError:
            BUY_PRICE = None
            SELL_PRICE = None
        if BUY_PRICE is not None and SELL_PRICE is not None:
            if BUY_PRICE <= current_price and SELL_PRICE > current_price:
                profit = SELL_PRICE - BUY_PRICE
                roi = (profit / BUY_PRICE) * 100 if BUY_PRICE != 0 else 0
                total_return_rate = ((SELL_PRICE - BUY_PRICE) / BUY_PRICE) * 100 if BUY_PRICE != 0 else 0
                result_message = "買入和賣出設定成功！"
                records.append({
                    'buy_price': BUY_PRICE,
                    'sell_price': SELL_PRICE,
                    'profit': profit,
                    'roi': round(roi, 2),
                    'total_return_rate': round(total_return_rate, 2)
                })
            elif BUY_PRICE <= current_price:
                profit = 0 
                roi = 0
                total_return_rate = 0
                result_message = "買入設定成功！"
                records.append({
                    'buy_price': BUY_PRICE,
                    'sell_price': None,
                    'profit': profit,
                    'roi': roi,
                    'total_return_rate': total_return_rate
                })
            elif SELL_PRICE > current_price:
                profit = 0  
                roi = 0
                total_return_rate = 0
                result_message = "賣出設定成功！"
                records.append({
                    'buy_price': None,
                    'sell_price': SELL_PRICE,
                    'profit': profit,
                    'roi': roi,
                    'total_return_rate': total_return_rate
                })
            else:
                result_message = "買入和賣出設定失敗！"

        elif BUY_PRICE is not None:
            if BUY_PRICE <= current_price:
                profit = 0
                roi = 0
                total_return_rate = 0
                result_message = "買入設定成功！"
                records.append({
                    'buy_price': BUY_PRICE,
                    'sell_price': None,
                    'profit': profit,
                    'roi': roi,
                    'total_return_rate': total_return_rate
                })
            else:
                result_message = "買入設定失敗！"

        elif SELL_PRICE is not None:
            if SELL_PRICE > current_price:
                profit = 0
                roi = 0
                total_return_rate = 0
                result_message = "賣出設定成功！"
                records.append({
                    'buy_price': None,
                    'sell_price': SELL_PRICE,
                    'profit': profit,
                    'roi': roi,
                    'total_return_rate': total_return_rate
                })
            else:
                result_message = "賣出設定失敗！"

        else:
            result_message = "請設定買入或賣出價格！"

        return redirect(url_for('trading_zone', stock_code=stock_code, current_price=current_price,
                                result_message=result_message))

    elif request.method == 'GET':
        stock_code = request.args.get('stock_code')
        current_price = float(request.args.get('current_price'))

        return render_template('trading_zone.html', stock_code=stock_code, current_price=current_price,
                               buy_price=BUY_PRICE, sell_price=SELL_PRICE, records=records, result_message=None)

if __name__ == '__main__':
    app.run(debug=True)
