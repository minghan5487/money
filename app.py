from datetime import date

import plotly.express as px
import plotly.io as pio
from flask import Flask, redirect, render_template, request, url_for

import twse_api
from stock_service import get_history, get_name, get_realtime, is_valid_code
from trading import evaluate_order

app = Flask(__name__)

state = {'buy_price': None, 'sell_price': None, 'records': []}


def parse_price(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None


def plot_html(fig):
    fig.update_layout(template='plotly_white', height=340, margin=dict(l=40, r=20, t=50, b=40))
    return pio.to_html(fig, full_html=False, include_plotlyjs=False, config={'displayModeBar': False})


def safe(func, *args):
    try:
        return func(*args)
    except Exception:
        return None


def render_index(error=None):
    return render_template('index.html', current_year=date.today().year, error=error,
                           taiex=safe(twse_api.get_taiex), top_volume=safe(twse_api.get_top_volume) or [])


@app.route('/')
def index():
    return render_index()


@app.route('/stock', methods=['POST'])
def stock():
    code = request.form['stock_code'].strip()
    year = request.form.get('year')
    month = request.form.get('month')

    if not is_valid_code(code):
        return render_index(f'找不到股票代碼 {code}')

    try:
        history = get_history(code, year, month)
    except Exception as e:
        return render_index(f'查詢 {code} 失敗：{e}')

    quote = safe(twse_api.get_quote, code)
    valuation = safe(twse_api.get_valuation, code)
    realtime = safe(get_realtime, code)

    current_price = (realtime or {}).get('price') or (quote or {}).get('close')

    price_plot = amount_plot = ''
    if not history.empty:
        price_plot = plot_html(px.line(history, x='日期', y='收盤價', title='收盤價'))
        amount_plot = plot_html(px.bar(history, x='日期', y='成交量(張)', title='成交量'))

    return render_template('stock.html', stock_code=code, name=quote['name'] if quote else get_name(code),
                           quote=quote, valuation=valuation, realtime=realtime, current_price=current_price,
                           price_plot=price_plot, amount_plot=amount_plot)


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
