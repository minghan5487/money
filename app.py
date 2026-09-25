from datetime import date

import plotly.express as px
import plotly.io as pio
from flask import Flask, redirect, render_template, request, url_for

from stock_service import get_history, get_realtime, get_stock_price, is_valid_code
from trading import evaluate_order

app = Flask(__name__)

state = {'buy_price': None, 'sell_price': None, 'records': []}

POPULAR = [('2330', '台積電'), ('2317', '鴻海'), ('2454', '聯發科'), ('2382', '廣達'), ('0050', '元大台灣50')]


def parse_price(value):
    try:
        return float(value) if value else None
    except ValueError:
        return None


def plot_html(fig):
    fig.update_layout(template='plotly_white', height=340, margin=dict(l=40, r=20, t=50, b=40))
    return pio.to_html(fig, full_html=False, include_plotlyjs=False, config={'displayModeBar': False})


def render_index(error=None):
    return render_template('index.html', current_year=date.today().year, popular=POPULAR, error=error)


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
        title, current_price, change = get_stock_price(code)
        summary, order_book = get_realtime(code)
        history = get_history(code, year, month)
    except Exception as e:
        return render_index(f'查詢 {code} 失敗：{e}')

    price_plot = amount_plot = ''
    if not history.empty:
        price_plot = plot_html(px.line(history, x='日期', y='收盤價', title='收盤價'))
        amount_plot = plot_html(px.bar(history, x='日期', y='成交量(張)', title='成交量'))

    change_pct = None
    if current_price and change is not None and current_price != change:
        change_pct = change / (current_price - change) * 100

    return render_template(
        'stock.html', stock_code=code, title=title, current_price=current_price, change=change, change_pct=change_pct,
        summary=None if summary is None else summary.iloc[0].to_dict(),
        order_book=None if order_book is None else order_book.to_dict('records'),
        price_plot=price_plot, amount_plot=amount_plot,
    )


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
