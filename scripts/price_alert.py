import sys

import twse_api
from stock_service import get_name, get_realtime, is_valid_code
from trading import evaluate_order


def ask_price(prompt):
    text = input(prompt).strip()
    return float(text) if text else None


if __name__ == '__main__':
    code = input('請輸入股票代碼：').strip()
    if not is_valid_code(code):
        sys.exit(f'找不到股票代碼 {code}')

    realtime = get_realtime(code)
    quote = twse_api.get_quote(code)
    current_price = (realtime or {}).get('price') or (quote or {}).get('close')
    if current_price is None:
        sys.exit('無法取得當前價格')

    print(f'{get_name(code)}：{current_price}')

    try:
        buy_price = ask_price('買入價格（留空略過）：')
        sell_price = ask_price('賣出價格（留空略過）：')
    except ValueError:
        sys.exit('請輸入數字')

    message, record = evaluate_order(current_price, buy_price, sell_price)
    print(message)
    if record and record['profit']:
        print(f"利潤：{record['profit']}，報酬率：{record['roi']}%")
