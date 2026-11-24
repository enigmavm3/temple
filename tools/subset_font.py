"""產生楷書子集 docs/fonts/kai-{hero,home,site}.woff2，並改寫 docs/site.css 裡的 @font-face 區塊。

字型來源：產品 repo religion 的 app/static/fonts/penglai-kai-base.ttf（Penglai Kai／蓬萊楷，
「全字庫正楷體」的子集並改名，SIL Open Font License 1.1；授權與來源說明見 docs/fonts/OFL.txt、docs/fonts/NOTICE）。
預設找本 repo 旁邊的 ../religion，可用環境變數 RELIGION_DIR 指定，或直接給字型檔路徑。

切成三份，以 unicode-range 讓瀏覽器只下載頁面用得到的那幾份：
  kai-hero：首頁首屏（頁首＋首屏區塊）的字，首頁會預載
  kai-home：首頁其他的字（首頁整頁內文都用楷書）
  kai-site：其他頁面用楷書的地方（標題、按鈕、選單、問題、標籤等）還缺的字

什麼時候要跑：改了 tools/build_html.py 的文案並重跑之後（新字沒進子集時會退回系統標楷體，不會壞版，只是字形不一）。
用法（在 repo 根目錄）：python tools/subset_font.py [字型檔.ttf]
需要：fonttools、brotli。
"""
import html
import io
import os
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CSS = DOCS / "site.css"
RELIGION = Path(os.environ.get("RELIGION_DIR", ROOT.parent / "religion"))
SRC = RELIGION / "app" / "static" / "fonts" / "penglai-kai-base.ttf"
FAMILY = "Penglai Kai"
BEGIN, END = "/* @font-face：由 tools/subset_font.py 產生，勿手改 */", "/* @font-face 結束 */"
# 標點與常用符號一律放進首屏那份（很小，避免到處各缺一點）
ALWAYS = "，。、：；？！「」『』（）…—・－　0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz $%&+-./:@"
# 分頁上用楷書的元素（要和 site.css 的 --kai 套用範圍一致）
KAI_TAGS = r"h1|h2|h3|summary|dt|th|figcaption|button"
KAI_CLASSES = r"kicker|seal|brand-name|btn|more|foot-h|step-no|lv-no|soon|nav|faq-toc|h-sub|price-what|honest"


def text_of(fragment: str) -> str:
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def chars(s: str) -> set:
    return {c for c in s if not c.isspace()}


def kai_text(page: str) -> str:
    page = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    out = [m.group(2) for m in re.finditer(rf"<({KAI_TAGS})\b[^>]*>(.*?)</\1>", page, re.S)]
    for m in re.finditer(rf'<(\w+)\b[^>]*class="[^"]*\b(?:{KAI_CLASSES})\b[^"]*"[^>]*>(.*?)</\1>', page, re.S):
        out.append(m.group(2))
    for m in re.finditer(r'<nav\b.*?</nav>', page, re.S):
        out.append(m.group(0))
    return text_of(" ".join(out))


def build(font_path: Path, text: str, out: Path) -> int:
    opts = subset.Options()
    opts.flavor = "woff2"; opts.layout_features = ["*"]; opts.name_IDs = ["*"]; opts.hinting = False
    opts.notdef_outline = True; opts.desubroutinize = True
    f = subset.load_font(str(font_path), opts)
    s = subset.Subsetter(opts); s.populate(text=text); s.subset(f)
    subset.save_font(f, str(out), opts)
    return out.stat().st_size


def ranges(cs) -> str:
    cps = sorted(ord(c) for c in cs)
    parts, i = [], 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1:
            j += 1
        parts.append(f"U+{cps[i]:X}" if i == j else f"U+{cps[i]:X}-{cps[j]:X}")
        i = j + 1
    return ", ".join(parts)


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    cmap = TTFont(str(src)).getBestCmap()
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    head = re.search(r'<header class="site-head">.*?</header>', index, re.S).group(0)
    hero = re.search(r'<section class="hero".*?</section>', index, re.S).group(0)
    hero_set = chars(text_of(head + hero)) | chars(ALWAYS)
    home_set = chars(text_of(index)) - hero_set
    site = set()
    for p in sorted(DOCS.glob("*.html")):
        if p.name != "index.html":
            site |= chars(kai_text(p.read_text(encoding="utf-8")))
    site_set = site - hero_set - home_set
    (DOCS / "fonts").mkdir(exist_ok=True)
    blocks, missing = [], set()
    for name, cs in [("hero", hero_set), ("home", home_set), ("site", site_set)]:
        have = {c for c in cs if ord(c) in cmap}
        missing |= cs - have
        size = build(src, "".join(sorted(have)), DOCS / "fonts" / f"kai-{name}.woff2")
        print(f"kai-{name}.woff2：{len(have)} 字，{size // 1024} KB")
        blocks.append(f'@font-face {{ font-family: "{FAMILY}"; src: url("fonts/kai-{name}.woff2") format("woff2"); '
                      f'font-weight: 400; font-display: swap;\n  unicode-range: {ranges(have)}; }}')
    if missing:
        print("字型裡沒有、會退回系統楷體的字：", "".join(sorted(missing)).encode("unicode_escape").decode())
    css = CSS.read_text(encoding="utf-8")
    a, b = css.index(BEGIN), css.index(END)
    css = css[:a] + BEGIN + "\n" + "\n".join(blocks) + "\n" + css[b:]
    CSS.write_text(css, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
