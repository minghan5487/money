def evaluate_order(current_price, buy_price=None, sell_price=None):
    if buy_price is None and sell_price is None:
        return '請設定買入或賣出價格！', None

    buy_ok = buy_price is not None and buy_price <= current_price
    sell_ok = sell_price is not None and sell_price > current_price

    if buy_ok and sell_ok:
        profit = round(sell_price - buy_price, 2)
        roi = round(profit / buy_price * 100, 2) if buy_price else 0
        return '買入和賣出設定成功！', {'buy_price': buy_price, 'sell_price': sell_price, 'profit': profit, 'roi': roi}
    if buy_ok:
        return '買入設定成功！', {'buy_price': buy_price, 'sell_price': None, 'profit': 0, 'roi': 0}
    if sell_ok:
        return '賣出設定成功！', {'buy_price': None, 'sell_price': sell_price, 'profit': 0, 'roi': 0}

    if buy_price is not None and sell_price is not None:
        return '買入和賣出設定失敗！', None
    return ('買入設定失敗！' if buy_price is not None else '賣出設定失敗！'), None
