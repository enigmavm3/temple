"""產生 docs/ 的 HTML、sitemap.xml（共用頁首頁尾）。

用法（在 repo 根目錄）：python tools/build_html.py
條款類四頁的內文與收費頁的價目，取自產品官網的快照 tools/source/product_site/*.html（文字不改）；
只在內文之外（標題日期下方）加站方公告。site.css、字型、圖片不由本程式產生。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "tools" / "source" / "product_site"   # 產品官網（religion 的 FastAPI 官網）渲染結果的快照
DOCS = ROOT / "docs"
BASE = "https://triplehai.com/temple/"
OLD = "https://web-production-36fe7bad.up.railway.app"
LINE = "https://line.me/R/ti/p/%40564szswh"
OG = BASE + "og-image.jpg"
SITE_DATE = "2026-11-24"

# 楷書：自架 Penglai Kai（全字庫正楷體的子集，OFL 1.1）。tools/subset_font.py 依頁面用字切成三份：
# kai-hero（首屏用字，預載）、kai-home（首頁其他用字）、kai-site（分頁標題等用字），以 unicode-range 按需下載。
def fonts(pre=""):
    return f'<link rel="preload" href="{pre}fonts/kai-hero.woff2" as="font" type="font/woff2" crossorigin>'


GA_ID = "G-6KMVJK1X1X"
# line_click：點到加好友連結（line.me、lin.ee）時送出；cta_position 取最近的 data-cta，沒有就用所在區塊的 id，再沒有就是 other
GA = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
      "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());"
      f"gtag('config','{GA_ID}');"
      "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*=\"line.me\"],a[href*=\"lin.ee\"]');if(!a)return;"
      "var c=a.closest('[data-cta]'),s=a.closest('section,article,header,footer');"
      "gtag('event','line_click',{link_url:a.href,page_path:location.pathname,cta_position:c?c.getAttribute('data-cta'):(s&&s.id)||'other'});},true);</script>")


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def crumbs(path, name):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "蓬萊仙闕", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": name, "item": BASE + path}]})


def head(*, path, title, desc, og_type="website", extra="", noindex=False, absolute=False, body_class=""):
    url = BASE + path
    pre = BASE if absolute else ""
    meta = [
        '<!doctype html>', '<html lang="zh-Hant-TW">', '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        GA,
        f'<title>{title}</title>',
        f'<meta name="description" content="{desc}">',
        '<meta name="theme-color" content="#faedda">',
    ]
    if noindex:
        meta.append('<meta name="robots" content="noindex">')
    else:
        meta += [
            f'<link rel="canonical" href="{url}">',
            f'<meta property="og:type" content="{og_type}">',
            '<meta property="og:site_name" content="蓬萊仙闕">',
            '<meta property="og:locale" content="zh_TW">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{desc}">',
            f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{OG}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:image:alt" content="蓬萊仙闕：宣紙上的水墨遠山與一輪淡朱色的日，寫著「心裡有事的時候，這裡有一炷香的安靜。」">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{title}">',
            f'<meta name="twitter:description" content="{desc}">',
            f'<meta name="twitter:image" content="{OG}">',
        ]
    meta += [
        f'<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">',
        f'<link rel="icon" href="{pre}favicon-32.png" type="image/png" sizes="32x32">',
        f'<link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">',
        fonts(pre),
        f'<link rel="stylesheet" href="{pre}site.css">',
    ]
    if extra:
        meta.append(extra)
    meta += ['</head>', f'<body class="{body_class}">' if body_class else '<body>', '<a class="skip" href="#main">跳到主要內容</a>']
    return "\n".join(meta)


def header(current="", absolute=False):
    pre = BASE if absolute else ""
    home = BASE if absolute else "./"

    def a(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{pre}{href}"{cur}>{label}</a>'

    return f"""
<header class="site-head">
  <a class="brand" href="{home}" aria-label="蓬萊仙闕首頁"><span class="seal" aria-hidden="true">仙</span><span class="brand-name">蓬萊仙闕</span></a>
  <nav class="nav" aria-label="主選單">
    {a("features.html", "功能", "features")}
    {a("plans.html", "收費", "plans")}
    {a("faq.html", "常見問題", "faq")}
    <a class="btn btn-line nav-cta" href="{LINE}" rel="noopener" data-cta="header">加 LINE 好友</a>
  </nav>
</header>
"""


CTA_TEXT = "加 LINE 好友，進廟靜一靜"
HONEST_FINE = "線上儀式體驗，廟公由 AI 扮演。沒有實體廟宇，與任何真實宮廟或宗教團體無關。"


def footer(absolute=False, dock=False):
    pre = BASE if absolute else ""
    home = BASE if absolute else "./"
    dock_html = ""
    if dock:
        dock_html = f"""
<div class="dock" aria-hidden="true"><a class="btn btn-line" href="{LINE}" rel="noopener" tabindex="-1" data-cta="dock">{CTA_TEXT}</a></div>
<script>(function(){{var d=document.querySelector(".dock"),t=document.querySelector("[data-hero-cta]");if(!d)return;if(!t||!("IntersectionObserver" in window)){{d.classList.add("show");return}}new IntersectionObserver(function(e){{var r=e[0];d.classList.toggle("show",!r.isIntersecting&&r.boundingClientRect.top<0)}}).observe(t)}})();</script>"""
    return f"""
<footer class="site-foot">
  <div class="foot-in">
    <div class="foot-brand">
      <a class="brand" href="{home}"><span class="seal" aria-hidden="true">仙</span><span class="brand-name">蓬萊仙闕</span></a>
      <p class="fine">{HONEST_FINE}</p>
    </div>
    <nav class="foot-links" aria-label="認識蓬萊仙闕">
      <p class="foot-h">認識蓬萊仙闕</p>
      <a href="{pre}features.html">功能介紹</a><a href="{pre}plans.html">收費方式</a><a href="{pre}faq.html">常見問題</a>
    </nav>
    <nav class="foot-links" aria-label="條款與客服">
      <p class="foot-h">條款與客服</p>
      <a href="{pre}terms.html">服務條款</a><a href="{pre}privacy.html">隱私權政策</a><a href="{pre}refunds.html">退款辦法</a><a href="{pre}contact.html">商家與客服</a>
    </nav>
    <p class="foot-co">營業主體：艾鐸有限公司<br>統一編號：62222415<br>客服信箱：<a href="mailto:contact@triplehai.com">contact@triplehai.com</a></p>
    <p class="copy">© 2026 蓬萊仙闕・艾鐸有限公司</p>
  </div>
</footer>{dock_html}
</body>
</html>
"""


def cta(attr="", cls="", pos=""):
    dc = f' data-cta="{pos}"' if pos else ""
    return f'<a class="btn btn-line{(" " + cls) if cls else ""}" href="{LINE}" rel="noopener"{attr}{dc}>{CTA_TEXT}</a>'


def img(name, alt, w, h, cls="", lazy=True, sizes=None):
    """sizes 有給就同時輸出 320w／原寸 srcset（場景圖才有 -320 版）。"""
    c = f' class="{cls}"' if cls else ""
    lz = ' loading="lazy" decoding="async"' if lazy else ""
    ss = f' srcset="img/{name}-320.webp 320w, img/{name}.webp {w}w" sizes="{sizes}"' if sizes else ""
    return f'<img{c} src="img/{name}.webp"{ss} alt="{alt}" width="{w}" height="{h}"{lz}>'


def scene(name, alt, sizes):
    return img(name, alt, 560, 840, sizes=sizes)


def write(name, html):
    assert not re.search(r'(href|src|srcset)="/', html), name
    (DOCS / name).write_text(html, encoding="utf-8", newline="\n")


def closing(title_html, body="", hero_cta=True):
    attr = ' data-hero-cta' if hero_cta else ""
    return f"""
<section class="closing" aria-labelledby="closing-title">
  <img class="closing-ink" src="img/ink-band.webp" alt="" width="1600" height="500" loading="lazy" decoding="async">
  <div>
    <h2 id="closing-title">{title_html}</h2>
    {cta(attr, pos="closing")}
    {body}
  </div>
</section>"""


def page_head(seal, kicker, h1, lead, extra=""):
    return f"""
<header class="page-head">
  <div class="wrap page-head-in">
    <div class="page-head-copy">
      <p class="kicker"><span class="seal sm" aria-hidden="true">{seal}</span>{kicker}</p>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>{extra}
    </div>
  </div>
</header>"""


# ---------------------------------------------------------------- 共用問答（答案取自線上版官網、服務條款與隱私權政策的原意）
Q_REAL = ("這是真的廟嗎？", "不是。蓬萊仙闕是一項線上服務，沒有實體廟宇，也與任何真實宮廟或宗教團體無關。廟裡的場景是製作的圖像，廟公由 AI 扮演。")
Q_KEEPER = ("廟公是真人嗎？他會記得我嗎？", "不是真人，廟公由 AI 扮演。他記得你最近幾天說過的事和求過的籤，隔幾天再來可以接著聊；隔太久的事可能要再跟他說一次。他陪你把事情想清楚、替你講解籤詩，但不代神明發言，也不替任何結果打包票；醫療、投資、法律與人身安全的事，還是要找合格的專業人士。")
Q_FREE = ("要錢嗎？要下載 App 嗎？", '不用下載，在 LINE 裡點開就是廟埕。進廟、上香、擲筊、求籤都不用錢，問廟公每天有免費次數。付費項目尚未開放，現在全部免費用。詳見<a href="plans.html">收費方式</a>。')
Q_PRIVACY = ("我跟廟公說的話，會被誰看到？", '你跟廟公說的話加密保存，用來回覆你、讓他下次接得上話。產生回覆時，內容會交給 AI 模型供應商處理，但不包含你的 LINE 識別碼、姓名或付款資料；我們不會出售你的資料，也不會拿去做本服務以外的行銷。廟公只在你傳訊息時回覆，不會主動傳訊息給你。想刪掉的時候，在聊天室輸入「刪除我的資料」，照提示確認後就會清掉。完整說明見<a href="privacy.html">隱私權政策</a>。')
Q_PAYNOW = ("現在可以付費嗎？", '還不行。付款功能尚未開放，目前廟裡的事都不用錢：進廟、上香、擲筊、求籤、每天燒一次金紙，以及每天幾次跟廟公說話。開放時會在本網站公告，品項與價格見<a href="plans.html">收費方式</a>。')
Q_LUCK = ("付了錢，擲筊或求籤會比較順嗎？", "不會。每一次擲筊、每一支籤，都是你當下親手擲出來、搖出來的，沒有人能事先安排，也不會因為有沒有付費、付多少而不同。付費項目只影響廟的樣子、芳名錄、可以跟廟公多聊幾次，以及燈牆上的一盞燈。")
Q_MONEY = ("付的錢用在哪裡？", "付款開放後，款項是購買本公司線上服務的費用，由本公司開立電子發票，不會轉交任何宗教團體，也不能用來抵稅。")
Q_REFUND = ("可以退款嗎？", '付款開放後，線上服務在付款後立即提供，原則上不受理無理由退款。重複扣款、付款成功卻沒有收到服務等情形，請來信，我們查明後處理。完整說明見<a href="refunds.html">退款辦法</a>。')
Q_LAMP = ("光明燈的金額為什麼可以自己填？付多一點有差嗎？", "光明燈是一項線上服務：在廟裡側殿的燈牆上，為一個名字點一盞燈，從付款當天起亮 365 天。價金由你自己決定，最低 100 元。不管付多少，燈亮的時間、燈位和燈的樣子都一樣；金額會像其他付費項目一樣，計入那間廟的成長點數，並在芳名錄記上一筆（芳名錄依金額由高到低排列；沒有選擇留名就顯示為匿名）。這不是對任何宗教團體的捐助，款項不轉交任何宗教團體，也不能用來抵稅。點燈目前尚未開放。")
Q_DEITY = ("可以換主神嗎？", "第一次進廟先選一位，之後隨時可以換。每一尊主神都有一間人人可拜的公廟，正殿的樣子各不相同。")
Q_NAME = ("廟名會用到真實宮廟的名字嗎？", "廟名一律不使用真實宮廟的名稱。")
Q_URGENT = ("遇到很急、很危險的事怎麼辦？", "本服務不提供醫療、投資、法律或其他專業意見。遇到這類問題，請找合格的專業人士；遇到危急情況，請立即撥打 110、119，或撥打 1925 安心專線。")


def faq_html(items):
    return "\n".join(f"    <details>\n      <summary>{q}</summary>\n      <p>{a}</p>\n    </details>" for q, a in items)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


# ---------------------------------------------------------------- 首頁（水墨：首屏 → 三幅掛軸 → 有些時候 → 怎麼開始 → 必要的疑問 → 結尾）
INDEX_TITLE = "蓬萊仙闕｜線上拜拜、祈福、求籤的 LINE 線上廟宇"
INDEX_DESC = "心裡有事的時候，打開 LINE 進廟：上一炷香、為掛念的人祈福、擲筊求籤問個方向，再跟 AI 廟公慢慢說。線上的儀式體驗，現在免費，不用下載 App。"

org = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "Organization", "@id": BASE + "#org", "name": "艾鐸有限公司", "taxID": "62222415", "url": BASE,
         "logo": BASE + "logo-512.png", "email": "contact@triplehai.com",
         "brand": {"@type": "Brand", "name": "蓬萊仙闕", "logo": BASE + "logo-512.png"},
         "address": {"@type": "PostalAddress", "streetAddress": "吳興街19號", "addressLocality": "信義區",
                     "addressRegion": "台北市", "addressCountry": "TW"},
         "sameAs": [LINE],
         "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": "contact@triplehai.com",
                          "availableLanguage": "zh-Hant"}},
        {"@type": "WebSite", "@id": BASE + "#site", "name": "蓬萊仙闕", "url": BASE, "inLanguage": "zh-Hant-TW",
         "publisher": {"@id": BASE + "#org"}},
    ],
}
# 首屏的靜態水墨（也是 WebGL 不能用時看到的畫面），依寬度二選一預載
HERO_M = 'srcset="img/ink-hero-m-640.webp 640w, img/ink-hero-m.webp 1024w" sizes="100vw"'
HERO_D = 'srcset="img/ink-hero-d-960.webp 960w, img/ink-hero-d.webp 1536w" sizes="100vw"'
preload = (f'<link rel="preload" as="image" type="image/webp" image{HERO_M.replace(" sizes", " imagesizes")} media="(max-width: 899px)" fetchpriority="high">\n'
           f'<link rel="preload" as="image" type="image/webp" image{HERO_D.replace(" sizes", " imagesizes")} media="(min-width: 900px)" fetchpriority="high">\n'
           + ld(org))

# 首頁四題：常見問題頁答案的精簡版（意思相同），完整版在 faq.html
HOME_FAQ = [
    ("這是真的廟嗎？", "不是。這是線上的儀式體驗，沒有實體廟宇，也與任何真實宮廟或宗教團體無關；廟裡的場景是繪製的圖像。"),
    ("廟公是真人嗎？", "不是，廟公由 AI 扮演。他陪你把事情想清楚、替你講解籤詩，但不代神明發言，也不替任何結果打包票。"),
    ("要錢嗎？", "現在都不用錢：進廟、上香、擲筊、求籤，每天也有幾次可以跟廟公說話。付費項目尚未開放。"),
    ("我說的話，誰看得到？", "加密保存，只用來回覆你。回覆時內容會交給 AI 模型供應商處理，但不含你的 LINE 識別碼與姓名；不會出售，也不拿去做其他行銷。在聊天室輸入「刪除我的資料」就能清掉。"),
]

index = head(path="", title=INDEX_TITLE, desc=INDEX_DESC, extra=preload, body_class="home") + header() + f"""
<main id="main">

<section class="hero" data-ink aria-labelledby="hero-title">
  <picture class="hero-art"><source media="(min-width: 900px)" {HERO_D}><img src="img/ink-hero-m.webp" {HERO_M} alt="" width="1024" height="1536" fetchpriority="high"></picture>
  <div class="hero-in">
    <h1 id="hero-title" class="hero-title" data-ink-guard><span>心裡有事的時候，</span><span>這裡有一炷香的安靜。</span></h1>
    <div class="hero-copy" data-ink-guard>
      <p class="eyebrow">LINE 線上廟宇‧線上拜拜</p>
      <p class="lead">睡不著的夜裡、掛念一個人的時候、拿不定主意之前，打開 LINE 進廟，上一炷香，靜一靜。</p>
      {cta(' data-hero-cta', 'btn-hero', pos="hero")}
      <p class="cta-note">線上儀式體驗‧廟公由 AI 扮演‧沒有實體廟宇<br>現在都不用錢，不用下載 App</p>
    </div>
  </div>
</section>

<section class="sec scrolls-sec" aria-labelledby="scrolls-title">
  <div class="wrap">
    <h2 id="scrolls-title" class="sec-quiet">在這裡，可以</h2>
    <div class="scrolls">
      <article class="scroll"><h3>心安</h3><p>心裡亂的時候，進廟坐一會兒，看一炷香的煙慢慢升起。</p><span class="scroll-seal" aria-hidden="true">安</span></article>
      <article class="scroll"><h3>祈福</h3><p>在心裡默念一個名字，為掛念的人上一炷香、燒一份金紙。</p><span class="scroll-seal" aria-hidden="true">福</span></article>
      <article class="scroll"><h3>問方向</h3><p>拿不定主意時，擲個筊、求支籤，廟公陪你把事情想清楚。</p><span class="scroll-seal" aria-hidden="true">問</span></article>
    </div>
    <p class="scrolls-note">也可以在燈牆為掛念的人點一盞燈（點燈為付費項目，尚未開放）。<br>擲筊、求籤的結果與有沒有付費無關；怎麼選，仍由你自己決定。</p>
  </div>
</section>

<section class="sec moments" aria-labelledby="moments-title">
  <div class="wrap">
    <h2 id="moments-title" class="sec-quiet">有些時候</h2>
    <ul class="moment-lines">
      <li>睡不著的夜裡。</li>
      <li>離家很遠的時候。</li>
      <li>要做決定之前。</li>
      <li>或者，只是想安靜一下。</li>
    </ul>
  </div>
</section>

<section class="sec start" id="start" aria-labelledby="start-title">
  <div class="wrap start-in">
    <div class="start-copy">
      <h2 id="start-title">怎麼開始</h2>
      <ol class="steps">
        <li><span class="step-no" aria-hidden="true">壹</span>加 LINE 好友</li>
        <li><span class="step-no" aria-hidden="true">貳</span>選一位主神</li>
        <li><span class="step-no" aria-hidden="true">參</span>上一炷香</li>
      </ol>
      <div class="start-actions">{cta(pos="start")}<a class="more" href="features.html">看看廟裡還有什麼</a></div>
    </div>
    <figure class="start-shot">
      <div class="phone painting">{img("screen-hall", "LINE 裡的蓬萊仙闕正殿畫面：神龕前有擲筊、上香兩個按鈕", 440, 952)}</div>
      <figcaption>LINE 裡的正殿（示範畫面）</figcaption>
    </figure>
  </div>
</section>

<section class="sec home-faq" id="faq" aria-labelledby="faq-title">
  <div class="wrap">
    <h2 id="faq-title">進廟之前</h2>
    <div class="faq">
{faq_html(HOME_FAQ)}
    </div>
    <a class="more" href="faq.html">看全部常見問題</a>
  </div>
</section>
""" + closing('<span class="nw">心裡有事，</span><span class="nw">進廟坐坐。</span>', hero_cta=False,
              body='<p class="honest">蓬萊仙闕是線上的儀式體驗：場景是繪製的圖像，廟公由 AI 扮演，沒有實體廟宇，也與任何真實宮廟或宗教團體無關。它陪你靜一靜、想一想，不保證任何結果。</p>') + """

</main>
<script src="ink.js" defer></script>
""" + footer(dock=True)
write("index.html", index)

# ---------------------------------------------------------------- 功能頁
FEAT_TITLE = "功能介紹｜線上上香、擲筊、求籤解籤、燒金紙｜蓬萊仙闕"
FEAT_DESC = "LINE 裡的線上廟宇：選一位主神，上香、擲筊、求六十甲子籤再請廟公解籤、燒金紙、看光明燈牆，還有記下每次參拜的參拜曆。進廟免費。"
PHOTO_SIZES = "(min-width: 900px) 320px, 58vw"


def feature(anchor, kicker_seal, kicker, title, body, media):
    return f"""
<section class="feature wrap" id="{anchor}" aria-labelledby="{anchor}-t">
  <div class="feature-media">{media}</div>
  <div>
    <p class="kicker"><span class="seal sm" aria-hidden="true">{kicker_seal}</span>{kicker}</p>
    <h2 id="{anchor}-t">{title}</h2>
    {body}
  </div>
</section>"""


def photo_phone(photo, photo_alt, screen, screen_alt):
    return (f'<div class="photo">{scene(photo, photo_alt, PHOTO_SIZES)}</div>'
            f'<div class="phone">{img("screen-" + screen, screen_alt, 440, 952)}</div>')


levels = [("第一級", "小祠", "建廟即有"), ("第二級", "單殿", "累計 300 點"), ("第三級", "三川殿", "累計 1,500 點"),
          ("第四級", "重簷大殿", "累計 5,000 點"), ("第五級", "鐘鼓樓大廟", "累計 10,000 點"),
          ("第六級", "三進大廟", "累計 30,000 點"), ("第七級", "金闕天宮", "累計 100,000 點")]
levels_html = "\n".join(
    f'    <li class="level">{img(f"level-{i + 1}", f"{no}：{name}", 640, 427)}<p class="lv-no">{no}</p><h3>{name}</h3><p class="lv-at">{at}</p></li>'
    for i, (no, name, at) in enumerate(levels))

free_band = f"""
<aside class="band" aria-label="免費使用">
  <div class="wrap band-in">
    <p><span class="seal sm" aria-hidden="true">免</span>上香、擲筊、求籤、跟廟公說話，現在都不用錢。</p>
    {cta(pos="band")}
  </div>
</aside>"""

features = head(path="features.html", title=FEAT_TITLE, desc=FEAT_DESC, extra=crumbs("features.html", "功能介紹")) + header("features") + """
<main id="main">""" + page_head("廟", "功能介紹", "一炷香、一對筊、一支籤",
                                  "線上拜拜不用下載，在 LINE 裡點開就是廟埕：上香、擲筊、求六十甲子籤、燒金紙，一步一步親手做。有想問的，回到聊天室跟 AI 廟公說。",
                                  ) \
  + feature("deities", "神", "主神", "三十尊主神，選一位供奉",
            "<p>媽祖、觀世音菩薩、關聖帝君、土地公、文昌帝君、月下老人……第一次進廟先選一位，之後隨時可以換。每一尊主神都有一間人人可拜的公廟，正殿的樣子各不相同。</p>\n    <p class=\"fine\">廟名一律不使用真實宮廟的名稱。</p>",
            '<div class="trio">' + img("hall-guanyin", "觀世音菩薩的正殿", 560, 840, sizes="(min-width: 900px) 170px, 30vw")
            + img("hall-mazu", "媽祖的正殿", 560, 840, sizes="(min-width: 900px) 170px, 30vw")
            + img("hall-guansheng", "關聖帝君的正殿", 560, 840, sizes="(min-width: 900px) 170px, 30vw") + "</div>") \
  + feature("incense", "香", "上香", "走到香爐前，持香三拜",
            "<p>走到香爐前，持香三拜，把香插進爐裡。每天來一次，廟裡的香火就多一分。</p>\n    <p>每人每天上香一次算 20 點，讓廟一點一點長大。</p>",
            photo_phone("censer", "廟埕的天公爐，爐裡插著點燃的香", "censer", "天公爐畫面，下方是「拿香」按鈕")) \
  + feature("jiao", "筊", "擲筊", "連續三個聖筊，才算應允",
            "<p>在正殿把想問的事放在心裡，擲出一對筊。連續三個聖筊，才算應允。</p>\n    <p>每一次擲筊，都是你當下親手擲出來的，沒有人能事先安排，也不會因為有沒有付費、付多少而不同。</p>",
            photo_phone("jiao", "雙手捧著一對紅色的筊", "hall", "正殿畫面，神龕前有「擲筊」「上香」兩個按鈕")) \
  + feature("qian", "籤", "求籤與解籤", "求一支六十甲子籤，再請廟公解說",
            "<p>搖一搖籤筒，取出一支六十甲子籤，再擲筊確認是不是這一支。</p>\n    <p>求到的籤，回到聊天室請廟公講解。籤詩的白話解說由 AI 產生，僅供參考。</p>",
            photo_phone("qian", "雙手捧著籤筒", "qian", "求籤畫面：供桌上的籤筒與一對筊，下方可寫想問的事")) \
  + feature("keeper", "問", "跟廟公說說話", "心裡的事，回到聊天室慢慢說",
            "<p>回到聊天室直接打字。廟公陪你把事情想清楚，也替你講解求到的籤。</p>\n    <p>廟公由 AI 扮演。他記得你最近幾天說過的事和求過的籤，隔幾天再來可以接著聊；隔太久的事可能要再跟他說一次。他不代神明發言，也不替任何結果打包票。醫療、投資、法律與人身安全的事，還是要找合格的專業人士。</p>\n    <p class=\"fine\">問廟公每天有 3 次免費（以 LINE 內顯示為準）；加購問事次數的功能尚未開放。</p>",
            f'<div class="photo">{scene("hall-guansheng", "關聖帝君的正殿，燭火明亮", PHOTO_SIZES)}</div>') \
  + free_band \
  + feature("gold", "金", "燒金紙", "在金爐前，把金紙一張一張送進去",
            "<p>捧著金紙在金爐前拜三拜，再把金紙一張一張送進爐裡，看著火光把它化去。</p>\n    <p>每天可以免費燒一次。另外選購金紙的功能尚未開放。</p>",
            photo_phone("burn", "金爐爐口火光正旺，手邊一疊金紙", "burn", "金爐畫面：「心裡默念想祈求的事，拜三拜」")) \
  + feature("lamp", "燈", '光明燈<span class="soon">點燈尚未開放</span>', "為掛念的人，點一盞燈",
            "<p>在側殿的燈牆為一個名字點一盞燈，亮一年。燈牆現在就能進去看；點燈屬於付費項目，尚未開放。</p>\n    <p>開放後，價金由你自己決定，最低 100 元；不管付多少，燈亮的時間、燈位和燈的樣子都一樣。</p>\n    <p class=\"fine\">燈上的名字若是別人的，請先取得對方同意；燈牆上對其他人只顯示遮蔽後的名字。</p>",
            f'<div class="phone phone-solo">{img("screen-lamp", "光明燈畫面：側殿燈牆上一格格燈位，已點的燈寫著遮蔽後的名字（示範資料）", 440, 952)}</div>') \
  + feature("calendar", "曆", "參拜曆", "每一次參拜，都替你記著",
            "<p>參拜曆只記你自己的上香、擲筊、求籤與問事，一個月翻開來就看得到。</p>\n    <p>曆上也標出歲時節俗與神明聖誕，依民間常見的說法整理，各地廟宇的日子可能不同。</p>",
            photo_phone("pillars", "廟門口的龍柱與匾額", "calendar", "參拜曆畫面：國曆與農曆對照，標出上香、擲筊、求籤、問事的日子")) \
  + f"""
<section class="feature wrap" id="build" aria-labelledby="build-t">
  <div>
    <p class="kicker"><span class="seal sm" aria-hidden="true">蓋</span>蓋廟<span class="soon">尚未開放</span></p>
    <h2 id="build-t">蓋一間自己的廟，從小祠蓋到金闕天宮</h2>
    <p class="notice-inline">蓋自己的廟需要蓋廟費，付款功能尚未開放；目前可以每天到公廟上香，看公廟一級一級長大。</p>
    <p>開放後，第一次蓋廟費滿 100 元，就能建造一間屬於你的廟，幫它取名字、在龍柱留名。之後每一筆蓋廟費、每一次上香，都讓它長大一點。公廟最高到第五級，再往上只有自己的廟才有。</p>
    <p>廟越大，開的殿越多：同祀的神明、廟裡的浮雕與彩繪作品，會隨著等級一一安座。</p>
  </div>
  <div class="feature-media"><div class="phone">{img("screen-home", "廟埕俯瞰畫面：點圖上的紅籤走進正殿、三川殿、廟埕、護龍", 440, 952)}</div><div class="photo photo-wide">{img("level-5", "第五級：鐘鼓樓大廟", 640, 427)}</div></div>
</section>
<div class="wrap">
  <ol class="levels" aria-label="廟的七個等級">
{levels_html}
  </ol>
  <p class="levels-note fine">蓋廟費 1 元算 1 點；每人每天上香一次算 20 點。點數只用來決定廟的樣子，不能兌換或轉讓。</p>
</div>
""" + closing('<span class="nw">心裡有事，</span><span class="nw">進廟坐坐。</span>',
              body='<p class="honest">進廟、上香、擲筊、求籤都不用錢。付費項目尚未開放，預計的品項見<a href="plans.html">收費方式</a>。</p>') + """
</main>
""" + footer(dock=True)
write("features.html", features)

# ---------------------------------------------------------------- 收費頁（價格照線上版；付款尚未開放）
src_index = (LIVE / "index.html").read_text(encoding="utf-8")
prices_block = re.search(r'<div class="prices">.*?\n  </div>', src_index, re.S).group(0)
prices_block = re.sub(r"<h3>(.*?)</h3>", r'<h3>\1<span class="soon">尚未開放</span></h3>', prices_block)
brief_block = re.search(r'<dl class="terms-brief">.*?</dl>', src_index, re.S).group(0).replace('href="/refund"', 'href="refunds.html"')
for old, new in [("<dd>在 LINE 裡進廟後選購，", "<dd>開放後，在 LINE 裡進廟選購，"),
                 ("<dd>付款確認後立刻反映在廟裡。", "<dd>開放後，付款確認即反映在廟裡。"),
                 ("<dd>付款完成後開立電子發票，", "<dd>開放後，每筆付款完成即開立電子發票，")]:
    assert old in brief_block, old
    brief_block = brief_block.replace(old, new)
PLANS_TITLE = "收費方式｜線上拜拜免費進廟、付費項目價格｜蓬萊仙闕"
PLANS_DESC = "蓬萊仙闕進廟、上香、擲筊、求籤都不用錢。蓋廟費、線香、金紙、問事費與光明燈尚未開放付款，這裡先列出開放後的品項與價格；全部一次付款、不會自動續扣。"
notice = """
      <div class="notice" role="note"><span class="seal" aria-hidden="true">告</span><p><strong>付款功能尚未開放。</strong>現在進廟、上香、擲筊、求籤、每天燒一次金紙、跟廟公說話，都不用錢。下面是開放後預計的品項與價格，實際以開放時 LINE 內購買頁為準。</p></div>"""
plans = head(path="plans.html", title=PLANS_TITLE, desc=PLANS_DESC, extra=crumbs("plans.html", "收費方式")) + header("plans") + """
<main id="main">""" + page_head("價", "收費", '<span class="nw">收費方式：</span><span class="nw">免費進廟，</span><span class="nw">付費項目一覽</span>',
                                  "進廟、上香、擲筊、求籤都不用錢，問廟公每天有免費次數。付費項目目前尚未開放；下面先列出開放後的品項與價格，全部是一次付款，不會自動續扣。",
                                  extra=notice) + f"""
<section class="sec" aria-labelledby="prices-title">
  <div class="wrap">
  <h2 id="prices-title" class="h-sub">付費項目與價格<small>開放後適用</small></h2>
  {prices_block}
  <h2 class="h-sub">怎麼買、交付與退款<small>開放後適用</small></h2>
  {brief_block}
  <p class="fine plan-note">付費項目只影響廟的樣子、芳名錄、可以問的次數，以及燈牆上有沒有你點的燈，和擲筊、求籤的結果無關。價格以開放後 LINE 內購買頁顯示為準。</p>
  <p class="fine">開放後，第一次蓋廟費滿 100 元，就能建造一間屬於你的廟。蓋廟費 1 元算 1 點；每人每天上香一次算 20 點。點數只用來決定廟的樣子，不能兌換或轉讓。等級說明見<a href="features.html#build">蓋自己的廟</a>。</p>
  </div>
</section>""" + closing('<span class="nw">先進廟看看，</span><span class="nw">不用錢。</span>') + """
</main>
""" + footer(dock=True)
write("plans.html", plans)

# ---------------------------------------------------------------- 常見問題
FAQ_TITLE = "常見問題｜線上求籤、擲筊準嗎？廟公是誰？｜蓬萊仙闕"
FAQ_DESC = "蓬萊仙闕常見問題：是不是真的廟、廟公是不是真人、現在要不要錢、付費會不會讓擲筊求籤比較順、光明燈怎麼算、說的話誰看得到、資料怎麼刪除。"
GROUPS = [("about", "關於這座廟", [Q_REAL, Q_NAME, Q_DEITY, Q_KEEPER]),
          ("pay", "擲筊、求籤與收費", [Q_PAYNOW, Q_FREE, Q_LUCK, Q_MONEY, Q_LAMP, Q_REFUND]),
          ("data", "資料與安全", [Q_PRIVACY, Q_URGENT])]
all_faq = [q for _, _, qs in GROUPS for q in qs]
faq_ld = ld({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "zh-Hant-TW",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in all_faq]})
groups_html = "\n".join(f'    <h2 class="faq-group" id="{gid}">{gname}</h2>\n{faq_html(qs)}' for gid, gname, qs in GROUPS)
toc = "".join(f'<a href="#{gid}">{gname}</a>' for gid, gname, _ in GROUPS)
faq = head(path="faq.html", title=FAQ_TITLE, desc=FAQ_DESC, extra=faq_ld + "\n" + crumbs("faq.html", "常見問題")) + header("faq") + """
<main id="main">""" + page_head("問", "常見問題", '<span class="nw">常見問題：</span><span class="nw">線上拜拜、</span><span class="nw">擲筊與求籤</span>',
                                  "是不是真的廟、要不要錢、說的話誰看得到，進廟之前先說清楚。") + f"""
<section class="sec" aria-label="問題列表">
  <div class="wrap faq-split">
    <nav class="faq-toc" aria-label="問題分類">
      <p class="foot-h">分類</p>{toc}
    </nav>
    <div class="faq">
{groups_html}
    <p class="fine faq-more">還有疑問嗎？請來信 <a href="mailto:contact@triplehai.com">contact@triplehai.com</a>，或看<a href="contact.html">商家資訊與客服</a>。</p>
    </div>
  </div>
</section>""" + closing('<span class="nw">心裡有事，</span><span class="nw">進廟坐坐。</span>') + """
</main>
""" + footer(dock=True)
write("faq.html", faq)

# ---------------------------------------------------------------- 條款類四頁：內文取自線上版，只改連結；內文之外加站方公告
SITE_NOTICE = ('\n  <p class="site-notice" role="note"><span class="seal sm" aria-hidden="true">告</span>'
               '<span><strong>公告：</strong>付款功能尚未開放，以下付款與退款相關內容自開放日起適用。</span></p>')
LINKS = {"/terms": "terms.html", "/privacy": "privacy.html", "/refund": "refunds.html", "/contact": "contact.html", "/": "./"}
doc_dates = {}
for live_name, out, crumb, with_notice in [("terms", "terms.html", "服務條款", True), ("privacy", "privacy.html", "隱私權政策", False),
                                           ("refund", "refunds.html", "退款辦法", True), ("contact", "contact.html", "商家資訊與客服", False)]:
    src = (LIVE / f"{live_name}.html").read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", src).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)">', src).group(1)
    article = re.search(r'<article class="doc">.*?</article>', src, re.S).group(0)
    article = article.replace(f"本網站（{OLD}）", "本網站（https://triplehai.com/temple）")
    for old, new in LINKS.items():
        article = article.replace(f'href="{old}"', f'href="{new}"')
    assert OLD not in article
    doc_dates[out] = re.search(r"最後更新：(\d{4}-\d{2}-\d{2})", article).group(1)
    if with_notice:
        article, n = re.subn(r'(<p class="doc-date">.*?</p>)', r"\1" + SITE_NOTICE.replace("\\", r"\\"), article, count=1)
        assert n == 1
    page = head(path=out, title=title, desc=desc, og_type="article", extra=crumbs(out, crumb)) + header() + f'\n<main id="main">\n{article}\n</main>\n' + footer()
    write(out, page)

# ---------------------------------------------------------------- 404（任何深度都會回這頁，站內網址寫完整網址）
p404 = head(path="404.html", title="找不到頁面｜蓬萊仙闕", desc="這個網址在蓬萊仙闕官網找不到對應的頁面，可能已經移動或輸入有誤。", noindex=True, absolute=True) \
    + header(absolute=True) + f"""
<main id="main">
<article class="doc">
  <p class="kicker"><span class="seal sm" aria-hidden="true">迷</span>找不到頁面</p>
  <h1>這裡沒有這一頁</h1>
  <p>這個網址找不到對應的頁面，可能已經移動或輸入有誤。</p>
  <p class="doc-actions"><a class="btn btn-ghost" href="{BASE}">回蓬萊仙闕首頁</a></p>
  <p class="doc-note">或看看<a href="{BASE}features.html">功能介紹</a>、<a href="{BASE}plans.html">收費方式</a>、<a href="{BASE}faq.html">常見問題</a>。</p>
</article>
</main>
""" + footer(absolute=True)
write("404.html", p404)

# ---------------------------------------------------------------- sitemap（條款頁的 lastmod 跟著頁面上的「最後更新」）
pages = [("", SITE_DATE), ("features.html", SITE_DATE), ("plans.html", SITE_DATE), ("faq.html", SITE_DATE)] + \
        [(p, doc_dates[p]) for p in ["terms.html", "privacy.html", "refunds.html", "contact.html"]]
(DOCS / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in pages) + "</urlset>\n",
    encoding="utf-8", newline="\n")
# 子路徑下的 robots.txt 不會被搜尋引擎讀取（只讀網域根目錄），不再產生；見 README「發佈」。
(DOCS / "robots.txt").unlink(missing_ok=True)
print("ok", doc_dates)
