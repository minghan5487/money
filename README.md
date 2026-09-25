# 台股查詢與交易試算平台

用 Flask 做的台股查詢網站，輸入股票代碼可以看即時報價、歷史走勢，並試算買賣價位的損益與報酬率。

## 功能

- 即時報價：爬 Yahoo 奇摩股市取得現價與漲跌
- 即時資訊：用 twstock 取得最新成交價、成交量、五檔買賣價量
- 歷史走勢：依年份 / 月份查詢，用 Plotly 畫收盤價與成交量圖
- 交易試算：設定買入 / 賣出價位，依現價判斷並計算利潤與報酬率

## 技術

Python、Flask、pandas、Plotly、twstock、BeautifulSoup、Bootstrap

## 專案結構

```
app.py              Flask 路由
stock_service.py    股價爬蟲、twstock 資料
trading.py          買賣判斷與報酬率計算
templates/          頁面
scripts/            命令列版本
```

## 執行

```bash
pip install -r requirements.txt
python app.py
```

開啟 http://127.0.0.1:5000 ，輸入股票代碼（例如 2330）。

命令列版本：

```bash
python -m scripts.realtime_info
python -m scripts.history_by_period
python -m scripts.price_alert
```

## 相關專案

- [ML](https://github.com/minghan5487/ML)：用決策樹預測股價走勢
