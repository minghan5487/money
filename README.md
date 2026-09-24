# 📈 台股查詢與交易試算平台

以 **Flask** 建置的台股資訊網站：輸入股票代碼即可查看即時報價、歷史走勢圖，並試算買賣價位的損益與報酬率。

> 個人專案｜整合網頁爬蟲、資料處理、互動式視覺化與 Web 開發

## 功能

| 功能 | 說明 |
|---|---|
| 即時報價 | 以 `requests` + `BeautifulSoup` 爬取 Yahoo 奇摩股市，取得現價與漲跌 |
| 即時五檔 / 盤中資訊 | 透過 `twstock` 取得最新成交價、成交量、五檔買賣價量 |
| 歷史走勢 | 依年份 / 月份查詢歷史資料，以 **Plotly** 繪製收盤價折線圖與成交量長條圖 |
| 交易試算 | 設定買入 / 賣出價位，依現價判斷條件並計算利潤、ROI 與總報酬率 |

## 技術

`Python` · `Flask` · `Jinja2` · `Bootstrap` · `twstock` · `pandas` · `Plotly` · `BeautifulSoup`

## 專案結構

```
app.py                  # Flask 路由：查詢、繪圖、交易試算
stock_service.py        # 資料層：Yahoo 股價爬蟲、twstock 即時 / 歷史資料
trading.py              # 商業邏輯：買賣條件判斷與報酬率計算
templates/
  index.html            # 首頁：輸入股票代碼與期間
  stock.html            # 查詢結果：即時資訊表格與互動圖表
  trading_zone.html     # 交易試算區
scripts/                # 命令列小工具（共用上方模組）
  realtime_info.py      # 即時資訊與走勢圖
  history_by_period.py  # 指定期間歷史資料
  price_alert.py        # 買賣價位試算
```

資料取得、商業邏輯與網頁路由分層，網頁版與命令列工具共用同一套判斷規則。

## 執行方式

```bash
pip install -r requirements.txt
python app.py
```

開啟瀏覽器前往 `http://127.0.0.1:5000`，輸入股票代碼（例如 `2330`）。

## 相關專案

- [ML｜台股走勢預測](https://github.com/minghan5487/ML)：以決策樹迴歸預測收盤價，規劃與本平台整合

---
作者：[吳明翰](https://minghan5487.github.io/my/)
