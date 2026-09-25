import sys

from stock_service import get_stock_price
from trading import evaluate_order


def ask_price(prompt):
    text = input(prompt).strip()
    return float(text) if text else None


if __name__ == '__main__':
    code = input('請輸入股票代碼：').strip()
    title, current_price, change = get_stock_price(code)
    if current_price is None:
        sys.exit('無法取得當前價格')

    print(f'{title}：{current_price}（{change}）')

    try:
        buy_price = ask_price('買入價格（留空略過）：')
        sell_price = ask_price('賣出價格（留空略過）：')
    except ValueError:
        sys.exit('請輸入數字')

    message, record = evaluate_order(current_price, buy_price, sell_price)
    print(message)
    if record and record['profit']:
        print(f"利潤：{record['profit']}，報酬率：{record['roi']}%")
