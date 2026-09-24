"""CLI：取得即時股價，設定買入 / 賣出價位並試算報酬率（與網頁版交易區使用相同規則）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stock_service import get_stock_price  # noqa: E402
from trading import evaluate_order  # noqa: E402


def ask_price(prompt):
    text = input(prompt).strip()
    return float(text) if text else None


if __name__ == '__main__':
    stock_code = input('請輸入股票代碼：').strip()
    title, current_price, change = get_stock_price(stock_code)

    if current_price is None:
        sys.exit('無法取得當前價格')
    print(f'{title}：{current_price}（{change if change is not None else "—"}）')

    try:
        buy_price = ask_price('請設定買入價格（留空略過）：')
        sell_price = ask_price('請設定賣出價格（留空略過）：')
    except ValueError:
        sys.exit('輸入的價格不是有效的數字，請重新執行。')

    message, record = evaluate_order(current_price, buy_price, sell_price)
    print(message)
    if record and record['profit']:
        print(f"預估利潤：{record['profit']}，報酬率：{record['roi']}%")
