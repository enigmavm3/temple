# temple

「蓬萊仙闕」（開在 LINE 裡的線上廟宇）的官網與條款頁，純靜態網站，對外網址 https://triplehai.com/temple/ 。

產品本體（LINE bot、LIFF、付款）在另一個 repo（`religion`），這裡只放官網。

## 內容

發佈的內容全部在 `docs/`：靜態 HTML，沒有框架，共用一份 `site.css`；每頁有 Google Analytics 4（見下方「流量追蹤」）。**`docs/` 的 HTML、sitemap、圖片與圖示是由 `tools/` 的產生器輸出的**（見下方「產生器」），改內容要改產生器再重跑，不要直接改 `docs/` 裡的 HTML，否則下次重跑會被蓋掉。字體不向外部載入：楷書用自架的 Penglai Kai（產品 repo 裡「全字庫正楷體」的子集並改名，SIL OFL 1.1，授權與來源見 `docs/fonts/OFL.txt`、`docs/fonts/NOTICE`），切成三份子集 `docs/fonts/kai-{hero,home,site}.woff2`，以 unicode-range 按需下載；首頁整頁（含內文）用楷書，其他頁的標題、按鈕、選單、問題用楷書，內文用各平台內建明體。楷書後備字型依序是 DFKai-SB、BiauKai、標楷體、Kaiti TC。

| 檔案 | 頁面 |
|---|---|
| `index.html` | 首頁（水墨）：首屏一句話＋加好友 → 三幅掛軸（心安／祈福／問方向）→ 有些時候 → 怎麼開始 → 進廟之前（四題）→ 結尾與誠實聲明 |
| `features.html` | 功能介紹：主神、上香、擲筊、求籤與解籤、跟廟公說話、燒金紙、光明燈、參拜曆、蓋自己的廟（七個等級） |
| `plans.html` | 收費方式：品項與價格（與產品官網一致，改價要同步） |
| `faq.html` | 常見問題（含 FAQPage 結構化資料） |
| `terms.html`、`privacy.html`、`refunds.html`、`contact.html` | 服務條款、隱私權政策、退款辦法、商家資訊與客服（內文沿用產品官網的版本） |
| `404.html` | 找不到頁面（站內網址寫完整網址，因為 GitHub Pages 在任何深度都回這一頁） |
| `sitemap.xml` | 搜尋引擎用（站在子路徑，`robots.txt` 放這裡不會被讀，見「發佈」） |
| `og-image.jpg` | 分享圖 1200×630 |
| `favicon.svg`、`favicon-32.png`、`apple-touch-icon.png`、`logo-512.png` | 圖示（「仙」字已轉外框，不靠裝置字型）；`logo-512.png` 也是結構化資料的 logo |
| `fonts/` | 楷書子集字型與授權 |
| `img/` | 首屏水墨山水（`ink-hero-m`／`ink-hero-d` 與 `-640`／`-960` 小圖）、內頁與結尾的遠山帶（`ink-band`）、宣紙纖維紋（`paper-grain`，可平鋪）、功能頁場景圖（主圖 560 寬＋`-320` 小圖）與 LINE 內實際畫面截圖（示範資料，webp） |
| `ink.js` | 首屏水墨上的雲霧與墨（自寫 WebGL，見下方「首屏水墨」） |

## 產生器（`tools/`）

| 檔案 | 產出 | 來源 |
|---|---|---|
| `tools/build_html.py` | `docs/*.html`、`docs/sitemap.xml` | 文案寫在程式裡；條款類四頁的內文與收費頁價目取自 `tools/source/product_site/*.html`（產品官網 `religion` 線上渲染結果的快照，文字不改） |
| `tools/build_img.py` | `docs/img/*.webp`（含水墨靜態圖）、`docs/og-image.jpg`（水墨版分享圖）、`favicon.svg`、`favicon-32.png`、`apple-touch-icon.png`、`logo-512.png` | 場景圖與楷書字型取自產品 repo `religion`（`app/static/img/`、`app/static/fonts/penglai-kai-base.ttf`），預設找本 repo 旁邊的 `../religion`，可用環境變數 `RELIGION_DIR` 指定；LINE 內畫面取自 `tools/source/liff/`（示範模式截圖，無損 webp）；水墨山水取自 `tools/source/ink/gen-*.webp`（codex 內建 image_gen 產生，以 webp q90 保存）；宣紙紋理由程式產生 |
| `tools/subset_font.py` | `docs/fonts/kai-{hero,home,site}.woff2`，並改寫 `docs/site.css` 開頭的 @font-face 區塊 | 字型來源是 `religion` 的 `app/static/fonts/penglai-kai-base.ttf`；依 `docs/*.html` 用到的字切三份（首頁首屏／首頁其他／分頁的楷書處）。改了文案就在 `build_html.py` 之後重跑；沒跑也不會壞版，缺的字會退回系統標楷體 |

`docs/site.css`（開頭的 @font-face 區塊除外）、`docs/ink.js`、`docs/fonts/OFL.txt`、`docs/fonts/NOTICE`、`docs/.nojekyll` 不由產生器輸出，直接改檔。

```sh
pip install pillow fonttools brotli
python tools/build_img.py      # 換圖時才需要（會清空重建 docs/img/）
python tools/build_html.py     # 改文案、條款快照、價格後
python tools/subset_font.py    # build_html 之後，讓楷書子集跟上新字
```

產品官網的條款或價格改版時，先更新 `tools/source/product_site/` 的快照（抓 `https://web-production-36fe7bad.up.railway.app/site-src/`、`/site-src/terms`、`/site-src/privacy`、`/site-src/refund`、`/site-src/contact` 的 HTML 存成 `index.html`、`terms.html`、`privacy.html`、`refund.html`、`contact.html`），再重跑 `build_html.py`。產品端舊的 `/`、`/terms` 等路徑已 301 轉到本站，不要再抓（會抓回本站自己的頁面）；來源頁的站內連結是本站完整網址，產生器會換回相對路徑。

站台在子路徑 `/temple/` 底下：頁內連結與資源一律用相對路徑（`href="terms.html"`），不要用 `/` 開頭；canonical、og:url、結構化資料與 sitemap 寫完整網址 `https://triplehai.com/temple/…`。

## 首屏水墨（`docs/ink.js`）

- 底圖是一幅水墨山水（生圖，`.hero-art` 的 `<img>`，手機直幅、桌機橫幅各一張）。上面疊兩層即時渲染：緩慢流動的雲霧，以及手指或滑鼠劃過時在紙上暈開、幾秒內慢慢淡去的墨。開場時有一滴墨在山腳的霧裡暈開，提示可以劃。
- 標題與首屏文字（標 `data-ink-guard` 的元素）範圍內，墨會淡到幾乎看不見；CSS 另在字後墊一層紙色柔光，字始終清楚。
- 自寫 WebGL1（墨的擴散、合成兩個小 shader），不用外部函式庫。畫布不接收點擊，不擋文字與按鈕；墨與底圖的對位照 CSS 的 `object-fit`／`object-position` 計算。
- 降級：不支援 WebGL、裝置記憶體或核心數 ≤ 2、開啟省流量、偏好減少動態 → 不啟動，就是那張靜態山水。分頁在背景或首屏捲出畫面時暫停；平均幀時間超過 26 ms 先降算圖解析度，最低一級仍超過 40 ms 就停在最後一格。
- 量測：瀏覽器主控台看 `window.__ink`（狀態、等級、平均幀時間 ms）。

## 流量追蹤（Google Analytics 4）

- 每頁（含 404）`<head>` 都有 gtag，評估 ID `G-6KMVJK1X1X`，與同公司其他官網共用（同網域 triplehai.com，以路徑 `/temple/` 區分產品）。寫法比照觀微閣官網。片段在 `tools/build_html.py` 的 `GA`。
- 事件 `line_click`：點到加好友連結（`a[href*="line.me"]`、`a[href*="lin.ee"]`）時送出，參數：
  - `link_url`：連結網址
  - `page_path`：所在頁面路徑（`location.pathname`）
  - `cta_position`：按鈕位置，取最近的 `data-cta`；沒有就用所在區塊的 id；再沒有就是 `other`。目前的值：`hero`（首屏）、`start`（首頁怎麼開始）、`closing`（各頁結尾）、`header`（頁首，桌機）、`dock`（手機底部常駐）、`band`（功能頁中段）、`contact`（商家資訊與客服頁內文）。
- 隱私權政策第四節（官網統計）已寫明使用 GA4，文字照產品官網。

## 關鍵字與對應頁面

| 頁面 | 主要關鍵字 |
|---|---|
| 首頁 | 線上拜拜、線上廟宇、LINE 拜拜、祈福、求籤（title、description 與首屏小標） |
| features.html | 線上上香、線上擲筊、線上求籤、六十甲子籤、解籤、燒金紙、光明燈、神明聖誕 |
| plans.html | 線上拜拜 收費、線香、金紙、蓋廟、光明燈 |
| faq.html | 線上求籤準嗎、線上擲筊、廟公、AI |

首頁調性：莊嚴、平靜，主打「心安、祈福、尋求方向」，寫成體驗與陪伴，不寫成效果承諾；功能細節放 features.html。

文案紅線：不暗示與任何真實宮廟有關、不保證結果、不寫付費會讓擲筊求籤比較順；不使用捐款、樂捐、香油錢、奉獻、功德、捐獻、捐贈、布施、隨喜等字；誠實寫明廟公由 AI 扮演、沒有實體廟宇。

## 發佈

GitHub Pages：repo 設定 → Pages → Source 選 `main` 分支的 `/docs` 資料夾。push 到 `main` 後幾分鐘內生效。`docs/.nojekyll` 讓 Pages 不跑 Jekyll。

前提：repo 名稱必須是 `temple`，而且放在已經把 `triplehai.com` 設為自訂網域的同一個 GitHub 帳號下，網址才會是 `https://triplehai.com/temple/`。

本機預覽（模擬 `/temple/` 子路徑）：

```sh
mkdir -p /tmp/preview && cp -r docs /tmp/preview/temple
python -m http.server 8000 -d /tmp/preview
# 開 http://localhost:8000/temple/
```

`python -m http.server` 不會回自訂 404；404 頁的站內網址寫的是正式網址，本機要看版面請直接開 `/temple/404.html`（樣式會向正式站取，正式站上線前看到的是無樣式版）。

### 上線後要做的事

1. **robots.txt 與 sitemap**：搜尋引擎只讀網域根目錄的 `https://triplehai.com/robots.txt`，放在 `/temple/` 底下的 robots.txt 不會生效，所以這裡不放。到 triplehai.com 根站的 repo，在它的 robots.txt 加一行 `Sitemap: https://triplehai.com/temple/sitemap.xml`（目前已列 translator、Lagerstroemia、zaoan，沒有 temple）。
2. **Search Console**：在 triplehai.com 資源手動提交 `https://triplehai.com/temple/sitemap.xml`，並對首頁做「網址審查 → 要求建立索引」。
3. **站外入口**：從既有官網（translator、Lagerstroemia、zaoan）的頁尾「其他產品」各加一個連到 `https://triplehai.com/temple/` 的連結，由各自的 repo／session 處理。
4. **404**：用一個不存在的深層網址（例如 `/temple/a/b/c`）確認會回這裡的 404 頁且樣式正常。
5. 分享圖：用 LINE、Facebook 分享一次首頁網址，確認預覽卡片的圖與文字。

## 修改條款或價格時要同步的地方

條款、隱私權政策、退款辦法的文字與產品內的購買流程是一組的，改這裡就要一起改產品：

1. 頁面上的「最後更新」日期與「版本」。
2. 產品（`religion` repo）的購買同意文字 `PURCHASE_CONSENT_TEXT`，以及條款版本 `TERMS_VERSION`（購買頁送出的版本必須與後端設定相同，使用者的同意紀錄以此版本為準）。
3. 價格以產品的商品目錄為準；`plans.html` 的價目取自 `tools/source/product_site/index.html` 快照，改價時更新快照再重跑 `tools/build_html.py`。
4. 重大變更（付費或退款規則）依服務條款第八條，生效前要先公告。
5. `sitemap.xml` 的 `<lastmod>` 由 `tools/build_html.py` 產生：一般頁面用程式裡的 `SITE_DATE`（改了內容要一起改），條款類頁面自動取頁面上的「最後更新」日期。
6. 付款已於 2026-11-25 開放：`plans.html`、`features.html`、`faq.html`、首頁的「尚未開放」字樣與告示，以及條款類頁面標題下方的站方公告都已拿掉（`site.css` 的 `.soon`、`.notice`、`.notice-inline`、`.site-notice` 樣式保留未用）。
