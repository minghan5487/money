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
    global BUY_PRICE, SELL_PRICE

    stock_code = request.form['stock_code']
    year = request.form.get('year')
    month = request.form.get('month')
    
    # 使用 Yahoo 獲取股票即時資料
    title, current_price, change = get_stock_price(stock_code)

    # 使用 twstock 獲取股票即時資料
    stock_realtime = t.realtime.get(stock_code)
    result = pd.DataFrame(stock_realtime).T.iloc[1:3]
    result.columns = ['股票代碼', '地區', '股票名稱', '公司全名', '現在時間', '最新成交價', '成交量', '累計成交量', 
                      '最佳5檔賣出價', '最佳5檔賣出量', '最佳5檔買進價', '最佳5檔買進量', '開盤價', '最高價', '最低價']

    # 使用 twstock 獲取股票歷史資料
    stock = t.Stock(stock_code)
    if year and month:
        period = stock.fetch(int(year), int(month))
    elif year:
        period = stock.fetch_from(int(year), 1)
    else:
        period = stock.fetch_31()
    
    data = pd.DataFrame(period)
    data.columns = ['日期','成交股數','成交量','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']

    # 製作收盤價折線圖
    fig_price = e.line(data, x='日期', y='收盤價', title=f'{stock_code} 收盤價')
    price_plot = pi.to_html(fig_price, full_html=False)

    # 製作成交量長條圖
    fig_amount = e.bar(data, x='日期', y='成交量', title=f'{stock_code} 成交量')
    amount_plot = pi.to_html(fig_amount, full_html=False)

    return render_template('stock.html', stock_code=stock_code, result=result.to_html(classes='table table-bordered table-striped text-center'), 
                           title=title, current_price=current_price, change=change, 
                           price_plot=price_plot, amount_plot=amount_plot)

@app.route('/trading_zone', methods=['POST', 'GET'])
def trading_zone():
    global BUY_PRICE, SELL_PRICE, records

    if request.method == 'POST':
        BUY_PRICE = float(request.form['buy_price']) if request.form['buy_price'] else None
        SELL_PRICE = float(request.form['sell_price']) if request.form['sell_price'] else None

        stock_code = request.form['stock_code']
        current_price = float(request.form['current_price'])

        if BUY_PRICE and SELL_PRICE:
            if BUY_PRICE > current_price and SELL_PRICE < current_price:
                profit = SELL_PRICE - BUY_PRICE
                roi = (profit / BUY_PRICE) * 100 if BUY_PRICE != 0 else 0
                result_message = "買入和賣出設定成功！"
                records.append({'buy_price': BUY_PRICE, 'sell_price': SELL_PRICE, 'profit': profit, 'roi': round(roi, 2)})
            elif BUY_PRICE > current_price or BUY_PRICE == current_price:
                profit = 0  # 如果只買入而未達到賣出條件，沒有收益
                roi = 0
                result_message = "買入設定成功！"
                records.append({'buy_price': BUY_PRICE, 'sell_price': None, 'profit': profit, 'roi': roi})
            elif SELL_PRICE < current_price:
                profit = 0  # 如果只賣出而未達到買入條件，沒有收益
                roi = 0
                result_message = "賣出設定成功！"
                records.append({'buy_price': None, 'sell_price': SELL_PRICE, 'profit': profit, 'roi': roi})
            else:
                profit = 0  # 買入和賣出條件都未達成，沒有收益
                roi = 0
                result_message = "買入和賣出設定失敗！"
                records.append({'buy_price': None, 'sell_price': None, 'profit': profit, 'roi': roi})

            return redirect(url_for('trading_zone', stock_code=stock_code, current_price=current_price,
                        buy_price=BUY_PRICE, sell_price=SELL_PRICE,
                        profit=profit, roi=roi, result_message=result_message))


    elif request.method == 'GET':
        stock_code = request.args.get('stock_code')
        current_price = float(request.args.get('current_price'))
        buy_price = BUY_PRICE
        sell_price = SELL_PRICE

        if buy_price is not None and sell_price is not None:
            profit = sell_price - buy_price
            roi = (profit / buy_price) * 100 if buy_price != 0 else 0
        else:
            profit = 0
            roi = 0

        return render_template('trading_zone.html', stock_code=stock_code, current_price=current_price,
                               buy_price=buy_price, sell_price=sell_price, profit=profit, roi=round(roi, 2),
                               records=records, result_message=None)
if __name__ == '__main__':
    app.run(debug=True)
