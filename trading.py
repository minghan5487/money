"""交易試算：依現價判斷買入 / 賣出設定是否成立，並計算利潤與報酬率。"""


def evaluate_order(current_price, buy_price=None, sell_price=None):
    """回傳 (訊息, 紀錄 dict 或 None)。

    規則：買入價 <= 現價 視為買入成立；賣出價 > 現價 視為賣出成立。
    兩者皆成立時計算 利潤 = 賣出價 - 買入價 與 報酬率 = 利潤 / 買入價。
    """
    if buy_price is None and sell_price is None:
        return '請設定買入或賣出價格！', None

    buy_ok = buy_price is not None and buy_price <= current_price
    sell_ok = sell_price is not None and sell_price > current_price

    if buy_ok and sell_ok:
        profit = round(sell_price - buy_price, 2)
        roi = round(profit / buy_price * 100, 2) if buy_price else 0
        return '買入和賣出設定成功！', {'buy_price': buy_price, 'sell_price': sell_price,
                                        'profit': profit, 'roi': roi}
    if buy_ok:
        return '買入設定成功！', {'buy_price': buy_price, 'sell_price': None, 'profit': 0, 'roi': 0}
    if sell_ok:
        return '賣出設定成功！', {'buy_price': None, 'sell_price': sell_price, 'profit': 0, 'roi': 0}

    if buy_price is not None and sell_price is not None:
        return '買入和賣出設定失敗！', None
    return ('買入設定失敗！' if buy_price is not None else '賣出設定失敗！'), None
