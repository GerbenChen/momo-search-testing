# momo 搜尋功能自動化測試

- **測試對象：** [momoshop.com.tw](https://www.momoshop.com.tw/) 的搜尋功能——真實上線的正式環境網站，沒有任何 mock 或 stub。
- **技術棧：** Playwright + Pytest。
- **架構：** Page Object Model + 設定檔驅動 + 集中式產出物管理（截圖／trace／日誌）+ GitHub Actions CI。

---

## Structure

```text
momo-search-testing/
├── config/
│   └── config.yaml
├── pages/
│   ├── base_page.py
│   ├── search_page.py          # 搜尋框、搜尋按鈕、自動完成
│   └── search_result_page.py   # 結果列表、模糊比對回退、分頁
├── reports/                     # 執行後自動產生：html/、logs/、screenshots/、traces/
├── tests/
│   ├── conftest.py
│   ├── test_search_api.py          # P0: API測試
│   ├── test_search_core.py         # P0：有效關鍵字、Enter 鍵
│   ├── test_search_page_state.py   # P1：關鍵字保留、頁面驗證
│   ├── test_search_edge_cases.py   # P0/P1/P2：反向測試、邊界情境、輸入驗證
│   └── test_search_navigation.py   # P1：自動完成、分頁
├── utils/
│   ├── artifact_manager.py
│   ├── config_reader.py
│   └── logger.py
├── .github/workflows/test.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Install

1. **建立虛擬環境**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **安裝相依套件**

   ```bash
   pip install -r requirements.txt
   ```

3. **安裝 Playwright 瀏覽器**

   ```bash
   playwright install chromium
   ```

---

## Config

`config/config.yaml`（關鍵字與行為皆可調整）：

```yaml
base_url: "https://www.momoshop.com.tw/main/Main.jsp"
search_base_url: "https://www.momoshop.com.tw/search/"
autocomplete_api_url: "https://apisearch.momoshop.com.tw/momoSearchCloud/moec/autocompleteKeywordV3"
default_search_keyword: "洗面乳"
no_match_keyword: "不存在的商品xyz999zzz"
xss_payload: "<script>alert(1)</script>"
keyword_with_whitespace: "  洗面乳  "
keyword_with_special_characters: "洗面乳/男用"

browser:
  headless: true
  channel: null
  locale: "zh-TW"
  viewport:
    width: 1440
    height: 900

timeout: 30000

debug:
  video: false
  trace: true
```

---

## Execute

```bash
# 執行全部測試
pytest

# 只執行 smoke 子集（最快、也最適合在每次 commit 時執行）
pytest -m smoke

# 執行單一檔案
pytest tests/test_search_core.py

# 以可見瀏覽器模式執行（需先修改 config.yaml：browser.headless: false）
pytest tests/test_search_core.py -s
```

HTML 測試報告會自動產生於 `reports/html/report.html`（已透過 `pytest.ini` 設定，不需額外加參數）。

`@pytest.mark.headed` 的測試（自動完成下拉選單）需要有頭瀏覽器才能通過，本機執行不需額外設定，CI 環境的處理方式見下方「CI/CD」。

---

## DEBUG

| 產出物 | 產生時機 | 儲存位置 |
|---|---|---|
| 截圖 | 每個測試（無論成功或失敗） | `reports/screenshots/<日期>/` |
| Trace | 僅失敗的測試 | `reports/traces/<日期>/` |
| 影片 | 僅當 `debug.video: true` 時 | `reports/videos/<日期>/` |
| 日誌 | 每次執行 | `reports/logs/test_<執行時間戳記>.log`（每次執行各自獨立一個檔案，不會互相覆蓋或混在一起） |

檢視 trace：`playwright show-trace reports/traces/<日期>/<trace_檔名>.zip`

