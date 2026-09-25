# 台股查詢與交易試算平台

用 Flask 做的台股查詢網站，串接臺灣證券交易所 OpenAPI，可以查看收盤行情、估值、即時五檔與歷史走勢，並試算買賣價位的損益與報酬率。

## 功能

- 首頁：加權指數、當日成交量排行（點選即可查詢）
- 個股：收盤價、漲跌幅、開高低、成交量、本益比、殖利率、股價淨值比
- 即時五檔與歷史走勢圖（依年份 / 月份查詢）
- 交易試算：設定買入 / 賣出價位，依現價判斷並計算利潤與報酬率

## 資料來源

| 資料 | 來源 |
|---|---|
| 個股收盤行情 | 證交所 OpenAPI `/exchangeReport/STOCK_DAY_ALL` |
| 本益比、殖利率、淨值比 | 證交所 OpenAPI `/exchangeReport/BWIBBU_ALL` |
| 加權指數 | 證交所 OpenAPI `/exchangeReport/FMTQIK` |
| 成交量排行 | 證交所 OpenAPI `/exchangeReport/MI_INDEX20` |
| 即時五檔、歷史走勢 | twstock |

OpenAPI 回傳的是全市場資料，程式會快取 10 分鐘，避免每次查詢都重新下載。OpenAPI 只提供上市股票，上櫃股票會只顯示即時資訊與走勢。

## 技術

Python、Flask、pandas、Plotly、twstock、Bootstrap 5

## 專案結構

```
app.py              Flask 路由
twse_api.py         證交所 OpenAPI 串接與快取
stock_service.py    twstock 即時與歷史資料
trading.py          買賣判斷與報酬率計算
templates/          頁面
scripts/            命令列版本
```

## 執行

```bash
pip install -r requirements.txt
python app.py
```

開啟 http://127.0.0.1:5000

命令列版本：

```bash
python -m scripts.realtime_info
python -m scripts.history_by_period
python -m scripts.price_alert
```

## 相關專案

- [ML](https://github.com/minghan5487/ML)：用決策樹預測隔日股價
