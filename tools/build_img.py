"""產生 docs/img/*.webp（含首屏水墨靜態圖）、docs/og-image.jpg 與圖示（favicon.svg、favicon-32.png、apple-touch-icon.png、logo-512.png）。

用法（在 repo 根目錄）：python tools/build_img.py
需要 Pillow 與 fonttools。場景圖與楷書字型取自產品 repo religion（預設是本 repo 旁邊的 ../religion，
可用環境變數 RELIGION_DIR 指定）；LINE 內畫面截圖取自 tools/source/liff/（示範模式截圖，無損 webp）；
水墨山水取自 tools/source/ink/gen-*.webp（codex image_gen 產生的原圖，以 webp q90 保存）。
宣紙紋理 img/paper-grain.webp 由程式產生（可平鋪的半透明纖維紋）。"""
import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parent.parent
RELIGION = Path(os.environ.get("RELIGION_DIR", ROOT.parent / "religion"))
R = RELIGION / "app" / "static" / "img"
L = ROOT / "tools" / "source" / "liff"
DOCS = ROOT / "docs"
OUT = DOCS / "img"
KAI = str(RELIGION / "app" / "static" / "fonts" / "penglai-kai-base.ttf")
CACHE = ROOT / "tools" / ".cache"
CACHE.mkdir(parents=True, exist_ok=True)
shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir(parents=True)
total = 0


def save(src, name, w, q=60, blur=0.0, crop=None):
    global total
    im = Image.open(src).convert("RGB")
    if crop: im = im.crop(crop)
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    p = OUT / f"{name}.webp"; im.save(p, "WEBP", quality=q, method=6)
    total += p.stat().st_size
    print(f"{name}.webp {w}x{h} {p.stat().st_size//1024}KB")


T, P = R / "temple", R / "pov"
INK = ROOT / "tools" / "source" / "ink"
# 首屏水墨山水（生圖）：手機直幅、桌機橫幅各一張＋小圖；WebGL 的墨與雲霧疊在上面
save(INK/"gen-m-1.webp", "ink-hero-m", 1024, 90)
save(INK/"gen-m-1.webp", "ink-hero-m-640", 640, 88)
save(INK/"gen-d-1.webp", "ink-hero-d", 1536, 84)
save(INK/"gen-d-1.webp", "ink-hero-d-960", 960, 88)
# 內頁抬頭與結尾的遠山帶：裁自桌機那張的山（左側本來就是留白）
save(INK/"gen-d-1.webp", "ink-band", 1200, 84, crop=(0, 250, 1536, 1000))

# 宣紙紋理：256×256 可平鋪、半透明的纖維與紙漿顆粒（先 3×3 平鋪再模糊、取中間一格，邊界才接得起來）
import random
rnd = random.Random(20261124)
T0 = 256
base = Image.new("L", (T0, T0))
base.putdata([rnd.randint(0, 255) for _ in range(T0 * T0)])
fib = Image.new("L", (T0, T0), 0); fd = ImageDraw.Draw(fib)
for _ in range(70):                                   # 細長纖維
    x, y = rnd.uniform(0, T0), rnd.uniform(0, T0); ln = rnd.uniform(8, 30); import math; a = rnd.uniform(0, math.pi)
    for dx in (-T0, 0, T0):
        for dy in (-T0, 0, T0):
            fd.line([(x + dx, y + dy), (x + dx + ln * math.cos(a), y + dy + ln * math.sin(a))], fill=rnd.randint(90, 200), width=1)
def tile_blur(im, r):
    big = Image.new("L", (T0 * 3, T0 * 3))
    for i in range(3):
        for j in range(3): big.paste(im, (i * T0, j * T0))
    return big.filter(ImageFilter.GaussianBlur(r)).crop((T0, T0, 2 * T0, 2 * T0))
grain = tile_blur(base, .8)
from PIL import ImageChops
alpha = ImageChops.add(grain.point(lambda v: max(0, v - 150) // 5), tile_blur(fib, .5).point(lambda v: v // 9))
paper = Image.new("RGBA", (T0, T0), (120, 96, 70, 0)); paper.putalpha(alpha)
pp = OUT / "paper-grain.webp"; paper.save(pp, "WEBP", quality=80, method=6)
print("paper-grain.webp", pp.stat().st_size // 1024, "KB")
# 儀式與場景（直式 2:3）：主圖 560 寬（細節多的殿內圖先輕微柔化再壓），另出 320 寬給小格
SCENES = [(P/"jiao_hold.webp", "jiao", 0), (P/"qian_hold.webp", "qian", 0), (P/"burn_hold_full.webp", "burn", .5),
          (T/"s_censer_l7_lit.webp", "censer", .5), (T/"s_hall_mazu_l7.webp", "hall-mazu", .85),
          (T/"s_hall_guanyin_l7.webp", "hall-guanyin", .7), (T/"s_hall_guansheng_l5.webp", "hall-guansheng", .7),
          (T/"s_gate_pillars_l7.webp", "pillars", .6)]
for src, name, blur in SCENES:
    save(src, name, 560, 54, blur)
    save(src, f"{name}-320", 320, 58, blur * .6)
# 七個等級（橫式）
for i in range(1, 8):
    save(T/f"l{i}.webp", f"level-{i}", 640, 62)
# LIFF 實際畫面（示範資料）
for n in ["home", "hall", "qian", "burn", "calendar", "censer", "lamp"]:
    save(L/f"{n}.webp", f"screen-{n}", 440, 66)
print("img total", total // 1024, "KB")

# ---------------------------------------------------------------- 分享圖 1200×630（水墨：右側遠山，左側留白寫字）
W, H = 1200, 630
og = Image.open(INK/"gen-d-1.webp").convert("RGB").resize((1200, 800), Image.LANCZOS).crop((0, 95, 1200, 95 + H))
INKC, RED = (32, 29, 26), (160, 44, 30)
d = ImageDraw.Draw(og)
d.text((80, 230), "蓬萊仙闕", font=ImageFont.truetype(KAI, 116), fill=INKC, anchor="ls")
# 朱印：仙
d.rectangle([84 + 4 * 116 + 18, 142, 84 + 4 * 116 + 18 + 70, 212], fill=RED)
d.rectangle([84 + 4 * 116 + 23, 147, 84 + 4 * 116 + 13 + 70, 207], outline=(240, 214, 186), width=2)
d.text((84 + 4 * 116 + 53, 177), "仙", font=ImageFont.truetype(KAI, 46), fill=(246, 230, 210), anchor="mm")
f_sub = ImageFont.truetype(KAI, 44)
d.text((84, 318), "心裡有事的時候，", font=f_sub, fill=INKC, anchor="ls")
d.text((84, 382), "這裡有一炷香的安靜。", font=f_sub, fill=INKC, anchor="ls")
d.line([(86, 440), (250, 440)], fill=(150, 140, 128), width=2)
d.text((86, 492), "LINE 線上廟宇　上香‧祈福‧求籤", font=ImageFont.truetype(KAI, 30), fill=(92, 84, 74), anchor="ls")
og.save(DOCS / "og-image.jpg", "JPEG", quality=82, optimize=True, progressive=True)
print("og", (DOCS / "og-image.jpg").stat().st_size // 1024, "KB")
og.resize((400, 210), Image.LANCZOS).save(CACHE / "og_400.png")  # 預覽用，不發佈

# ---------------------------------------------------------------- 圖示：「仙」字轉外框
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ft = TTFont(KAI); gs = ft.getGlyphSet(); gname = ft.getBestCmap()[ord("仙")]
upm = ft["head"].unitsPerEm
g = gs[gname]
from fontTools.pens.boundsPen import BoundsPen
bp = BoundsPen(gs); g.draw(bp); xmin, ymin, xmax, ymax = bp.bounds
size = 40; s = size / upm
gw, gh = (xmax - xmin) * s, (ymax - ymin) * s
tx = 32 - gw / 2 - xmin * s; ty = 32 + gh / 2 + ymin * s  # y 軸翻轉
sp = SVGPathPen(gs); g.draw(TransformPen(sp, (s, 0, 0, -s, tx, ty)))
path = sp.getCommands()
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0" stop-color="#cf3a2e"/><stop offset="1" stop-color="#7f1712"/></linearGradient></defs>'
       '<rect x="4" y="4" width="56" height="56" rx="7" fill="url(#g)" stroke="#f3deaa" stroke-opacity=".6" stroke-width="2"/>'
       f'<path fill="#f3deaa" d="{path}"/></svg>')
(DOCS / "favicon.svg").write_text(svg, encoding="utf-8", newline="\n")
print("favicon.svg", len(svg) // 1024, "KB")


def icon_png(px, name, pad_ratio=0.0, rounded=True):
    k = 4; S = px * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bg = Image.new("RGB", (S, S))
    dd = ImageDraw.Draw(bg)
    for y in range(S):
        t = y / S
        dd.line([(0, y), (S, y)], fill=(int(207 + (127 - 207) * t), int(58 + (23 - 58) * t), int(46 + (18 - 46) * t)))
    mask = Image.new("L", (S, S)); md = ImageDraw.Draw(mask)
    if rounded: md.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * .12), fill=255)
    else: md.rectangle([0, 0, S, S], fill=255)
    im.paste(bg, (0, 0), mask)
    d2 = ImageDraw.Draw(im)
    inset = int(S * .07)
    d2.rounded_rectangle([inset, inset, S - inset, S - inset], radius=int(S * .08), outline=(243, 222, 170, 150), width=max(2, S // 90))
    fnt = ImageFont.truetype(KAI, int(S * .66))
    d2.text((S / 2, S / 2 + S * .02), "仙", font=fnt, fill=(243, 222, 170, 255), anchor="mm")
    im = im.resize((px, px), Image.LANCZOS)
    if not rounded: im = im.convert("RGB")
    im.save(DOCS / name, optimize=True)
    print(name, (DOCS / name).stat().st_size // 1024, "KB")


icon_png(512, "logo-512.png", rounded=False)
icon_png(180, "apple-touch-icon.png", rounded=False)
icon_png(32, "favicon-32.png")
