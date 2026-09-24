from datetime import date

import plotly.express as px
import plotly.io as pio
from flask import Flask, redirect, render_template, request, url_for

from stock_service import get_history, get_realtime_table, get_stock_price
from trading import evaluate_order

app = Flask(__name__)

# 示範用：交易設定與紀錄存在記憶體中，重新啟動即清空
state = {'buy_price': None, 'sell_price': None, 'records': []}


def _parse_price(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None


@app.route('/')
def index():
    return render_template('index.html', current_year=date.today().year)


@app.route('/stock', methods=['POST'])
def stock():
    stock_code = request.form['stock_code'].strip()
    year = request.form.get('year')
    month = request.form.get('month')

    try:
        title, current_price, change = get_stock_price(stock_code)
        realtime = get_realtime_table(stock_code)
        history = get_history(stock_code, year, month)
    except Exception as exc:  # 網路或資料來源異常時回首頁顯示錯誤
        return render_template('index.html', current_year=date.today().year,
                               error=f'查詢 {stock_code} 失敗：{exc}')

    price_plot = amount_plot = ''
    if not history.empty:
        price_plot = pio.to_html(px.line(history, x='日期', y='收盤價', title=f'{stock_code} 收盤價'),
                                 full_html=False)
        amount_plot = pio.to_html(px.bar(history, x='日期', y='成交量', title=f'{stock_code} 成交量'),
                                  full_html=False)

    result = realtime.to_html(classes='table table-bordered table-striped text-center') if realtime is not None else ''
    return render_template('stock.html', stock_code=stock_code, title=title,
                           current_price=current_price, change=change, result=result,
                           price_plot=price_plot, amount_plot=amount_plot)


@app.route('/trading_zone', methods=['GET', 'POST'])
def trading_zone():
    if request.method == 'POST':
        stock_code = request.form['stock_code']
        current_price = float(request.form['current_price'])
        state['buy_price'] = _parse_price(request.form.get('buy_price'))
        state['sell_price'] = _parse_price(request.form.get('sell_price'))

        message, record = evaluate_order(current_price, state['buy_price'], state['sell_price'])
        if record:
            state['records'].append(record)
        return redirect(url_for('trading_zone', stock_code=stock_code,
                                current_price=current_price, result_message=message))

    stock_code = request.args.get('stock_code')
    current_price = _parse_price(request.args.get('current_price'))
    if not stock_code or current_price is None:
        return redirect(url_for('index'))

    return render_template('trading_zone.html', stock_code=stock_code, current_price=current_price,
                           buy_price=state['buy_price'], sell_price=state['sell_price'],
                           records=state['records'], result_message=request.args.get('result_message'))


if __name__ == '__main__':
    app.run(debug=True)
