from flask import Flask, render_template, request
import twstock as t
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock', methods=['POST'])
def stock():
    stock_code = request.form['stock_code']
    start_year = int(request.form.get('start_year', '2024'))
    start_month = int(request.form.get('start_month', '1'))
    end_year = int(request.form.get('end_year', '2024'))
    end_month = int(request.form.get('end_month', '12'))
    
    stock = t.Stock(stock_code)

    # Fetching data for the specified period
    if start_year == end_year and start_month == end_month:
        period = stock.fetch(start_year, start_month)
    else:
        period = stock.fetch_from(start_year, start_month)
        
    data = pd.DataFrame(period)
    data.columns = ['日期', '成交股數', '成交量', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']

    # Line chart for closing prices
    fig_price = px.line(data, x='日期', y='收盤價', title=f'{stock_code} 收盤價')
    price_plot = pio.to_html(fig_price, full_html=False)

    # Bar chart for trading volume
    fig_amount = px.bar(data, x='日期', y='成交量', title=f'{stock_code} 成交量')
    amount_plot = pio.to_html(fig_amount, full_html=False)

    # Real-time stock data
    stock_realtime = t.realtime.get(stock_code)
    if stock_realtime['success']:
        realtime_data = {
            '最新成交價': stock_realtime['realtime']['latest_trade_price'],
            '成交量': stock_realtime['realtime']['accumulate_trade_volume'],
            '最佳五檔買進價': stock_realtime['realtime']['best_bid_price'],
            '最佳五檔買進量': stock_realtime['realtime']['best_bid_volume'],
            '最佳五檔賣出價': stock_realtime['realtime']['best_ask_price'],
            '最佳五檔賣出量': stock_realtime['realtime']['best_ask_volume']
        }
    else:
        realtime_data = None

    return render_template('stock.html', stock_code=stock_code, price_plot=price_plot, amount_plot=amount_plot, realtime_data=realtime_data)

if __name__ == '__main__':
    app.run(debug=True)
