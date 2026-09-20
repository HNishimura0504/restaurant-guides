# -*- coding: utf-8 -*-
"""**地図を持たないガイドに、店舗マップとその直下の目次を差し込む。**

ユーザー指示（2026-09-20）「**全ての既存のガイドに現在の最新のルールを適応して**」。
未適用だったのは**欧州8冊に店舗マップが無い**こと＝
規約 `playbook.md` §7 [2026-08-02]「**店舗マップ機構を標準装備化**」が、それより前に作った8冊に及んでいなかった。

**なぜ `build_html.py` で作り直さないか**: 欧州8冊は `control/` に `locations_*.json` しか無く、
再生成に要る4種（`meta_`/`places_`/`research_`/`photo_pick_`）が揃っていない（B-343 と同じ形）。
**なぜ `retoc_html.py` を使わないか**: あれは**既にある地図のピンで目次を振り分け直す**もので、
**地図が無いところへ地図を入れる用途には使えない。**

**だからこのスクリプトは「HTMLを読んで、HTMLに差し込む」だけで完結させる。**
本文（店カード）には一切触らない。触るのは ①`<style>` への規則の追加 ②目次ブロックの置き換え の2か所だけ。

タイルは **OpenStreetMap（無料・キー不要）**。Google Maps Platform は使わない（2026-09-16 ユーザー指示）。
帰属表記 `Map © OpenStreetMap contributors` を画像に焼き込む（規約 §7 [2026-08-02]）。

**ピンのタップ範囲**は規約 §2 の落とし穴 2b・2c を最初から満たす:
  ・`.mapwrap` は `overflow:visible`（`hidden` だと縁のピンの外半分が切られて 3mm を割る）
  ・アンカーは中心基準 `translate(-50%,-50%)` ＋ `min-width/min-height:4.6mm`
  ・左右端のピンは内側へクランプ（ページ余白側へはみ出した分が切られるため）
"""
import io, json, math, os, re, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TILE = 256
UA = {"User-Agent": "restaurant-guides/1.0 (personal food guide; github.com/HNishimura0504)"}
CACHE = Path("/tmp/claude-0/-home-user/e86ca3d9-1a2f-51c7-aef4-ed39de70a5e5/scratchpad/tile_cache")

# 断面の CSS クラス → 色。欧州8冊の `<style>` が使っている var 名に合わせる。
CLS_COLOR = {"be": "blue", "fr": "blue", "ch": "aqua", "sw": "yellow", "br": "violet",
             "bi": "beer", "eu": "blue", "me": "aqua", "af": "yellow", "as": "violet",
             "la": "red", "rt": "blue", "wd": "blue"}
HEX = {"blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100",
       "violet": "#4a3aa7", "beer": "#0d366b", "red": "#e34948"}

# 本文幅 105.5mm（@page 120mm − 左右 7mm）。地図はこれ以内に収める。
BODY_MM = 105.5
PAD_MM = 2.3   # 端のピンを内側へ寄せる量（クランプ）

CSS = """
/* --- 店舗マップ（2026-09-20 追加・規約 §7 [2026-08-02] の標準装備を遡及適用） --- */
.mapsec{break-inside:avoid; margin:0 0 3mm;}
.mapttl{font-size:10.5pt; font-weight:bold; margin:1mm 0 1.5mm;}
/* overflow:hidden にすると地図の縁に立つピンのタップ範囲が切られて 3mm を割るため、
   角丸は画像側に付け、wrapper は overflow:visible のままにする（規約 §2 の落とし穴 2b）。 */
.mapwrap{position:relative; border:1px solid var(--line); border-radius:2mm;
         break-inside:avoid; margin-left:auto; margin-right:auto;}
.mapwrap img{display:block; width:100%; border-radius:2mm;}
.mapwrap a{position:absolute; display:block; transform:translate(-50%,-50%);
           min-width:4.6mm; min-height:4.6mm;}
.mapnote{font-size:7.5pt; color:#75736d; margin-top:1mm;}
.tn{display:inline-block; min-width:5.5mm; text-align:center; color:#fff; border-radius:99px;
    font-size:8pt; padding:.2mm 1.4mm; margin-right:1.2mm;}
"""


def key(sid):
    """HTML のアンカー id（`c-foo`）→ `locations_*.json` のキー（`foo`）。"""
    return sid[2:] if sid.startswith("c-") else sid


def deg2xy(lat, lng, z):
    n = 2.0 ** z
    x = (lng + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def fetch_tile(z, x, y):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / ("%d_%d_%d.png" % (z, x, y))
    if p.exists():
        return Image.open(p).convert("RGB")
    req = urllib.request.Request("https://tile.openstreetmap.org/%d/%d/%d.png" % (z, x, y), headers=UA)
    d = urllib.request.urlopen(req, timeout=30).read()
    p.write_bytes(d)
    time.sleep(0.4)           # タイルサーバへの礼儀（規約の帰属表記とセット）
    return Image.open(p).convert("RGB")


def build_map(title, cards, locs, out_png, maxz=15, bbox=None):
    """cards = [(sid, name, cls), …] の出現順。番号は掲載順そのもの。"""
    # **`locations_*.json` のキーは `c-` を持たない**（HTML のアンカー id だけが `c-` を付ける）。
    # ここを取り違えると「座標が無い店 36件」と出て全滅する（2026-09-20 実測で踏んだ）。
    pts = [(i + 1, sid, cls, locs[key(sid)])
           for i, (sid, name, cls) in enumerate(cards) if key(sid) in locs]
    if not pts:
        return None
    if bbox:
        # 拡大図は**枠内の店だけ**を描く（規約 §7 [2026-09-05]「拡大図＝枠内の店だけ」）。
        # ただし**番号は全域図と同じ**にする＝掲載順の通し番号なので、ここで振り直さない。
        b0, b1, c0, c1 = bbox
        pts = [p for p in pts if b0 <= p[3]["lat"] <= b1 and c0 <= p[3]["lng"] <= c1]
        if len(pts) < 3:
            return None
    lats = [p[3]["lat"] for p in pts]
    lngs = [p[3]["lng"] for p in pts]
    la0, la1, lo0, lo1 = min(lats), max(lats), min(lngs), max(lngs)
    # 余白を1割足す（ピンが縁に立つと読みにくい）
    dla = max((la1 - la0) * 0.12, 0.002)
    dlo = max((lo1 - lo0) * 0.12, 0.002)
    la0, la1, lo0, lo1 = la0 - dla, la1 + dla, lo0 - dlo, lo1 + dlo

    # **縦横比が極端なときは横へ広げる。** 店が南北に細長く散る都市（ヘント・リエージュで実測）では
    # 縦長の地図になり、紙面の高さに収めようとして**幅が 56mm まで縮み、地図そのものが読めなくなる**。
    # 縮めるのではなく**経度の範囲を広げて比を寝かせる**＝地図は 105.5mm 幅のまま、周辺が余分に写るだけ。
    # 比は「メルカトルの投影後」で見る（緯度が高いほど経度1度は短い）。
    ASPECT = 1.55
    cosl = math.cos(math.radians((la0 + la1) / 2))
    h = (la1 - la0)
    w = (lo1 - lo0) * cosl
    if w > 0 and h / w > ASPECT:
        need = h / ASPECT / cosl
        cx = (lo0 + lo1) / 2
        lo0, lo1 = cx - need / 2, cx + need / 2

    # 1300px 以内に収まる最大のズームを選ぶ（紙面 105mm に載る解像度）
    for z in range(maxz, 9, -1):
        x0, y1 = deg2xy(la0, lo0, z)
        x1, y0 = deg2xy(la1, lo1, z)
        if (x1 - x0) * TILE <= 1300 and (y1 - y0) * TILE <= 1500:
            break
    x0, y1 = deg2xy(la0, lo0, z)
    x1, y0 = deg2xy(la1, lo1, z)
    tx0, ty0, tx1, ty1 = int(x0), int(y0), int(x1) + 1, int(y1) + 1
    img = Image.new("RGB", ((tx1 - tx0) * TILE, (ty1 - ty0) * TILE), "#e8e4dd")
    for tx in range(tx0, tx1):
        for ty in range(ty0, ty1):
            try:
                img.paste(fetch_tile(z, tx, ty), ((tx - tx0) * TILE, (ty - ty0) * TILE))
            except Exception as e:
                print("    tile skip %d/%d/%d: %s" % (z, tx, ty, str(e)[:40]))
    img = img.crop((int((x0 - tx0) * TILE), int((y0 - ty0) * TILE),
                    int((x1 - tx0) * TILE), int((y1 - ty0) * TILE)))
    W, H = img.size
    dr = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    pins = []
    R = 12
    for num, sid, cls, loc in pts:
        px, py = deg2xy(loc["lat"], loc["lng"], z)
        x = (px - x0) / (x1 - x0) * W
        y = (py - y0) / (y1 - y0) * H
        color = HEX.get(CLS_COLOR.get(cls, "blue"), "#2a78d6")
        dr.ellipse([x - R, y - R, x + R, y + R], fill=color, outline="white", width=2)
        t = str(num)
        tb = dr.textbbox((0, 0), t, font=font)
        dr.text((x - (tb[2] - tb[0]) / 2, y - (tb[3] - tb[1]) / 2 - tb[1]), t, fill="white", font=font)
        pins.append({"sid": sid, "num": num, "cx": x / W * 100, "cy": y / H * 100})
    dr.rectangle([W - 280, H - 20, W, H], fill="white")
    dr.text((W - 274, H - 17), "Map © OpenStreetMap contributors", fill="#333", font=font)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return {"file": out_png.name, "title": title, "w": W, "h": H, "pins": pins}


def dense_bbox(cards, locs):
    """**外れ値に引っ張られて中心部が潰れるとき**に使う、中心の密集域の枠を返す。

    実測で踏んだ形（2026-09-20 リエージュ）＝**1店だけ 25.7km 離れている**ために
    全域図が郊外まで広がり、**市街の35店が左上の数%に固まって番号が読めなくなった**。

    判定＝**全域の広がりが、四分位範囲（IQR）から作った枠の 2.5 倍を超えるか。**
    平均や標準偏差ではなく**四分位**を使う＝外れ値そのものに判定を歪められないため。
    超えないなら拡大図は要らない（`None` を返す）。
    """
    import statistics
    pts = [locs[key(sid)] for sid, _, _ in cards if key(sid) in locs]
    if len(pts) < 8:
        return None
    la = sorted(p["lat"] for p in pts)
    lo = sorted(p["lng"] for p in pts)

    def q(xs, f):
        return xs[min(len(xs) - 1, max(0, int(len(xs) * f)))]

    cosl = math.cos(math.radians(statistics.median(la)))
    iqr_la = q(la, 0.75) - q(la, 0.25)
    iqr_lo = (q(lo, 0.75) - q(lo, 0.25)) * cosl
    full_la = la[-1] - la[0]
    full_lo = (lo[-1] - lo[0]) * cosl
    span_iqr = max(iqr_la, iqr_lo, 1e-9)
    span_full = max(full_la, full_lo)
    if span_full < span_iqr * 2.5:
        return None
    # 中心＝四分位の中点。半径＝IQR の 1.6 倍（最低 1.2km ぶん）。
    cla = (q(la, 0.25) + q(la, 0.75)) / 2
    clo = (q(lo, 0.25) + q(lo, 0.75)) / 2
    rla = max(iqr_la * 1.6, 1.2 / 111.0)
    rlo = max(iqr_lo * 1.6, 1.2 / 111.0) / cosl
    return (cla - rla, cla + rla, clo - rlo, clo + rlo)


def sections_and_cards(s):
    """本文を出現順に走査して、見出しと店カードを拾う。**本文は書き換えない。**"""
    items = []
    for m in re.finditer(r'<h2[^>]*id="(s-[^"]+)"[^>]*>(.*?)</h2>'
                         r'|<div class="card" id="(c-[^"]+)">', s, re.S):
        if m.group(1):
            items.append(("h", m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()))
        else:
            cid = m.group(3)
            tail = s[m.end():m.end() + 1500]
            nm = re.search(r'<div class="nm">(.*?)(?:<span class="yomi">|</div>)', tail, re.S)
            items.append(("c", cid, re.sub(r"<[^>]+>", "", nm.group(1)).strip() if nm else cid[2:]))
    return items


def toc_block(items, pinnum, n, only=None):
    """地図の直下に置く目次。番号バッジはピンと同じ数字・同じ色。"""
    out = ['<div class="toc">',
           '  <div class="th">この地図の店（%d店・番号はピンと同じ）</div>' % n]
    buf = []
    cur_cls = "be"

    def flush():
        if buf:
            out.append('  <div class="links">')
            out.extend(buf)
            out.append("  </div>")
            del buf[:]

    for kind, ident, text in items:
        if kind == "h":
            flush()
            cur_cls = ident[2:]
            out.append('  <div class="sec %s"><a href="#%s" style="all:unset;cursor:pointer;">%s</a></div>'
                       % (cur_cls, ident, text))
        else:
            num = pinnum.get(ident)
            if num is None or (only is not None and ident not in only):
                continue
            color = HEX.get(CLS_COLOR.get(cur_cls, "blue"), "#2a78d6")
            buf.append('    <a href="#%s"><span class="tn" style="background:%s;">%d</span>%s</a>'
                       % (ident, color, num, text))
    flush()
    out.append("</div>")
    return "\n".join(out)


def replace_toc(s, new_html):
    """既存の `.toc` ブロックを、括弧の対応で範囲を取って丸ごと差し替える。
    **素朴な find だと入れ子の `</div>` で切れる**ので、必ず深さを数える。"""
    if '<div class="toc">' not in s:
        # **地図を作り直したときは、剥がしたあとに目次が残っていない。**
        # その場合は最初の章見出しの直前へ入れる（元の地図もそこに在った）。
        m = re.search(r'<h2[^>]*id="s-', s)
        if not m:
            raise SystemExit("差し込み先が見つからない")
        return s[:m.start()] + new_html + "\n\n" + s[m.start():], ""
    start = s.index('<div class="toc">')
    depth, i = 0, start
    while True:
        m = re.compile(r"<div\b|</div>").search(s, i)
        if not m:
            raise SystemExit("目次の終わりが見つからない")
        depth += 1 if m.group(0) == "<div" else -1
        i = m.end()
        if depth == 0:
            return s[:start] + new_html + s[i:], s[start:i]


def strip_maps(s):
    """既にある地図セクションと、その直下の目次を全部取り除く。

    **元の題は覚えておいて使い回す**（「中心部拡大(一ノ関駅〜大町・地主町)」のように
    人が付けた題が入っていることがあり、機械が付け直すと情報が落ちるため）。
    """
    titles = [re.sub(r"（.*", "", t).strip()
              for t in re.findall(r'<div class="mapttl">🗺?🗾?\s*店舗マップ\s*—\s*([^<]*)', s)]
    while '<div class="mapsec">' in s:
        i = s.index('<div class="mapsec">')
        depth, j = 0, i
        while True:
            m = re.compile(r"<div\b|</div>").search(s, j)
            depth += 1 if m.group(0) == "<div" else -1
            j = m.end()
            if depth == 0:
                break
        # 直後に続く目次（.toc）も一緒に取る
        k = re.match(r'\s*<div class="toc">', s[j:])
        if k:
            depth, jj = 0, j + k.start()
            while True:
                m = re.compile(r"<div\b|</div>").search(s, jj)
                depth += 1 if m.group(0) == "<div" else -1
                jj = m.end()
                if depth == 0:
                    break
            j = jj
        s = s[:i].rstrip() + "\n" + s[j:].lstrip("\n")
    return s, titles


def process(path, rebuild=False):
    s = io.open(path, encoding="utf-8").read()
    d = os.path.dirname(path)
    city = os.path.basename(path)[:-5]
    old_titles = []
    if '<div class="mapsec">' in s:
        if not rebuild:
            print("%-34s 既に地図あり — 飛ばす" % path)
            return 0
        s, old_titles = strip_maps(s)
    locs = json.load(io.open(os.path.join(d, "control", "locations_%s.json" % city), encoding="utf-8"))
    items = sections_and_cards(s)
    cards = [(i[1], i[2], "be") for i in items if i[0] == "c"]
    # カードの属する見出しのクラスを引き当てる
    cur = "be"
    cards = []
    for kind, ident, text in items:
        if kind == "h":
            cur = ident[2:]
        else:
            cards.append((ident, text, cur))
    missing = [c[0] for c in cards if key(c[0]) not in locs]
    if missing:
        print("%-34s 座標が無い店 %d 件 — 中止" % (path, len(missing)))
        return 0

    out_png = Path(d) / "img" / city / "_map.png"
    mp = build_map(old_titles[0] if old_titles else "全域マップ", cards, locs, out_png)
    if not mp:
        print("%-34s 地図を作れなかった" % path)
        return 0
    pinnum = {p["sid"]: p["num"] for p in mp["pins"]}
    maps = [mp]
    bb = dense_bbox(cards, locs)
    if bb:
        mp2 = build_map(old_titles[1] if len(old_titles) > 1 else "中心部拡大",
                        cards, locs, Path(d) / "img" / city / "_map2.png",
                        maxz=16, bbox=bb)
        if mp2:
            maps.append(mp2)

    # 地図ごとに「地図 → その直下の目次」を1組ずつ並べる
    # （規約 §7 [2026-09-05]「目次は**地図ごとにその直下**。単独の目次は地図の無いガイドだけ」）。
    blocks = []
    for k, m in enumerate(maps):
        # 実寸（mm）。縦長すぎると1ページに収まらないので幅を縮める。
        w_mm = BODY_MM
        h_mm = w_mm * m["h"] / m["w"]
        if h_mm > 150:                  # @page 240mm − 余白 − 見出し・注記
            h_mm = 150.0
            w_mm = h_mm * m["w"] / m["h"]
        px = PAD_MM / w_mm * 100
        py = PAD_MM / h_mm * 100
        anchors = []
        for p in m["pins"]:
            cx = min(max(p["cx"], px), 100 - px)
            cy = min(max(p["cy"], py), 100 - py)
            anchors.append('    <a href="#%s" style="left:%.2f%%;top:%.2f%%;width:%.2f%%;height:%.2f%%;"></a>'
                           % (p["sid"], cx, cy, px * 2, py * 2))
        here = {p["sid"] for p in m["pins"]}
        blocks.append("\n".join([
            '<div class="mapsec">',
            '  <div class="mapttl">🗺️ 店舗マップ — %s（ピンをタップで各店のページへ）</div>' % m["title"],
            '  <div class="mapwrap" style="width:%.1fmm;">' % w_mm,
            '    <img src="img/%s/%s" alt="%s">' % (city, m["file"], m["title"]),
        ] + anchors + [
            "  </div>",
            '  <div class="mapnote">Map © OpenStreetMap contributors／ピンの番号は下の一覧と同じ</div>',
            "</div>",
            toc_block(items, pinnum, len(m["pins"]), only=here),
        ]))
    mapsec = "\n".join(blocks)

    s2, old = replace_toc(s, mapsec)
    if ".mapsec{" not in s2:
        s2 = s2.replace("</style>", CSS + "</style>", 1)
    io.open(path, "w", encoding="utf-8").write(s2)
    print("%-34s ピン %3d / 地図 %d枚 / 全域 %dx%d → %.1fmm" %
          (path, len(mp["pins"]), len(maps), mp["w"], mp["h"], w_mm))
    return 1


def main():
    args = [a for a in sys.argv[1:] if a != "--rebuild"]
    rebuild = "--rebuild" in sys.argv
    targets = args or sorted(p for p in __import__("glob").glob("europe/*/*.html"))
    n = 0
    for t in targets:
        n += process(t, rebuild)
    print("\n地図を入れた記事: %d 本" % n)


if __name__ == "__main__":
    main()
