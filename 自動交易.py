import requests
from bs4 import BeautifulSoup

# 使用 BeautifulSoup 從 Yahoo 股市獲取資料
def get_stock_price(stock_code):
    url = f'https://tw.stock.yahoo.com/quote/{stock_code}'
    web = requests.get(url)
    soup = BeautifulSoup(web.text, "html.parser")

    title = soup.find('h1').get_text()
    price_element = soup.select_one('.Fz\\(32px\\)')
    status_element = soup.select_one('.Fz\\(20px\\)')

    if price_element:
        current_price_text = price_element.get_text().strip().replace(',', '')
        try:
            current_price = float(current_price_text)
        except ValueError:
            current_price = None
    else:
        current_price = None

    if status_element:
        status = status_element.get_text().strip()
    else:
        status = "無法找到狀態"

    return title, current_price, status

def notify_success(action):
    print(f"{action} 設定成功！")

def notify_failure(action):
    print(f"{action} 設定失敗！")

# 自定義輸入股票代碼
stock_code = input("請輸入股票代碼：")

# 獲取當前股票價格
title, current_price, status = get_stock_price(stock_code)

# 輸出當前股票價格和狀態
if current_price is not None:
    print(f'{title} : {current_price} ( {status} )')
else:
    print("無法獲得當前價格")

# 繼續設定買入和賣出價格，並模擬下單
if current_price is not None:
    try:
        BUY_PRICE = float(input("請設定買入價格："))
        SELL_PRICE = float(input("請設定賣出價格："))

        # 模擬下單過程
        if BUY_PRICE > current_price and SELL_PRICE < current_price:
            notify_success("買入和賣出")
        elif BUY_PRICE > current_price or BUY_PRICE == current_price:
            notify_success("買入")
        elif SELL_PRICE < current_price:
            notify_success("賣出")
        else:
            notify_failure("買入和賣出")
        print(f"設定買入價格：{BUY_PRICE}")
        print(f"設定賣出價格：{SELL_PRICE}")
    except ValueError:
        print("輸入的價格不是有效的數字，請重新執行程序。")
