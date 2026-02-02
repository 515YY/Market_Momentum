# Market Momentum Dashboard

這是一個即時監控台股資金動能的 Dashboard，整合了產業細項與 MoneyDJ 概念股分類。

## 功能特色
- **熱點資金動能圖表**：視覺化顯示目前最強勢的產業與題材。
- **雙重分類標籤**：同時包含「產業細項」(如 IC設計) 與「概念題材」(如 AI PC, 5G)。
- **完整篩選功能**：點擊圖表或標籤即可篩選相關個股。

## 如何更新資料
1. 確保 `StockList.csv` 為最新狀態。
2. (選擇性) 若要更新概念股清單，執行 `update_concepts.py`。
3. 執行 `conclude_data.py` 生成新的 `dashboard_data.js`。
4. 開啟 `index.html` 查看結果。

## 線上預覽
(若已開啟 GitHub Pages)
https://515YY.github.io/Market_Momentum/
