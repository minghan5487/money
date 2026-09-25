from datetime import date

import plotly.express as px
import plotly.io as pio
from flask import Flask, redirect, render_template, request, url_for

from stock_service import get_history, get_realtime, get_stock_price, is_valid_code
from trading import evaluate_order

app = Flask(__name__)

state = {'buy_price': None, 'sell_price': None, 'records': []}


def parse_price(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None


def plot_html(fig):
    return pio.to_html(fig, full_html=False)


@app.route('/')
def index():
    return render_template('index.html', current_year=date.today().year)


@app.route('/stock', methods=['POST'])
def stock():
    code = request.form['stock_code'].strip()
    year = request.form.get('year')
    month = request.form.get('month')

    if not is_valid_code(code):
        return render_template('index.html', current_year=date.today().year, error=f'找不到股票代碼 {code}')

    try:
        title, current_price, change = get_stock_price(code)
        summary, order_book = get_realtime(code)
        history = get_history(code, year, month)
    except Exception as e:
        return render_template('index.html', current_year=date.today().year, error=f'查詢 {code} 失敗：{e}')

    price_plot = amount_plot = ''
    if not history.empty:
        price_plot = plot_html(px.line(history, x='日期', y='收盤價', title=f'{code} 收盤價'))
        amount_plot = plot_html(px.bar(history, x='日期', y='成交量(張)', title=f'{code} 成交量'))

    table_cls = 'table table-bordered table-striped text-center'
    result = ''
    if summary is not None:
        result = summary.to_html(classes=table_cls, index=False) + order_book.to_html(classes=table_cls, index=False)

    return render_template('stock.html', stock_code=code, title=title, current_price=current_price,
                           change=change, result=result, price_plot=price_plot, amount_plot=amount_plot)


@app.route('/trading_zone', methods=['GET', 'POST'])
def trading_zone():
    if request.method == 'POST':
        code = request.form['stock_code']
        current_price = float(request.form['current_price'])
        state['buy_price'] = parse_price(request.form.get('buy_price'))
        state['sell_price'] = parse_price(request.form.get('sell_price'))

        message, record = evaluate_order(current_price, state['buy_price'], state['sell_price'])
        if record:
            state['records'].append(record)
        return redirect(url_for('trading_zone', stock_code=code, current_price=current_price, result_message=message))

    code = request.args.get('stock_code')
    current_price = parse_price(request.args.get('current_price'))
    if not code or current_price is None:
        return redirect(url_for('index'))

    return render_template('trading_zone.html', stock_code=code, current_price=current_price,
                           buy_price=state['buy_price'], sell_price=state['sell_price'],
                           records=state['records'], result_message=request.args.get('result_message'))


if __name__ == '__main__':
    app.run(debug=True)
