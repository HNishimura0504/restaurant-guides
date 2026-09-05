# -*- coding: utf-8 -*-
"""美食ガイドの HTML を Notion 用 Markdown へ変換する。

リポジトリ直下の <region>/<country>/<city>.html を走査し、
  notion/guides_md/<region>_<country>_<city>.partNN.md
  notion/img_manifest.json
を作る。各店カードの見出し直後に @@IMG:<repo相対パス>@@ を置く（sync.py が実画像に差し替える）。

使い方:  python notion/build_md.py
"""
import io
import os
import re
import json
import html as htmllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "notion", "guides_md")
MANIFEST = os.path.join(ROOT, "notion", "img_manifest.json")
MAX_CHUNK = 19000
SKIP_DIRS = {".git", ".github", "notion"}


def _mklink(href, text):
    text = re.sub(r"<[^>]+>", "", text)
    text = htmllib.unescape(text).strip()
    href = htmllib.unescape(href).strip()
    if href.startswith("tel:") or href.startswith("#") or not href:
        return text
    return "[%s](%s)" % (text.replace("[", "").replace("]", ""), href)


def strip_tags(s, keep_links=True):
    if keep_links:
        s = re.sub(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                   lambda m: _mklink(m.group(1), m.group(2)), s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s).replace(" ", " ")
    return re.sub(r"[ \t]+", " ", s).strip()


def esc(s):
    """Notion 本文で記号として解釈される文字を無害化。"""
    return s.replace("*", "＊")


def split_cards(block):
    """<div class="card"> の出現位置で切る（閉じタグの書き方がガイドで違うため）。"""
    idx = [m.start() for m in re.finditer(r'<div class="card"[^>]*>', block)]
    for i, st in enumerate(idx):
        seg = block[st:(idx[i + 1] if i + 1 < len(idx) else len(block))]
        h2 = re.search(r"<h2\b", seg)
        yield seg[:h2.start()] if h2 else seg


def parse_cards(block):
    out = []
    for c in split_cards(block):
        m = re.search(r'<div class="nm">(.*?)</div>', c, re.S)
        if not m:
            continue
        card = {}
        nm = m.group(1)
        pin = re.search(r'class="pinno"[^>]*>(\d+)</span>', nm)
        card["no"] = pin.group(1) if pin else ""
        yomi = re.search(r'<span class="yomi">(.*?)</span>', nm, re.S)
        card["yomi"] = strip_tags(yomi.group(1), False) if yomi else ""
        nm2 = re.sub(r'<span class="pinno".*?</span>', "", nm, flags=re.S)
        nm2 = re.sub(r'<span class="yomi">.*?</span>', "", nm2, flags=re.S)
        card["name"] = strip_tags(nm2, False)

        m = re.search(r'<div class="chips">(.*?)</div>', c, re.S)
        card["chips"] = [strip_tags(x, False) for x in
                         re.findall(r'<span class="chip[^"]*">(.*?)</span>', m.group(1), re.S)] if m else []

        m = re.search(r'<div class="desc">(.*?)</div>', c, re.S)
        card["desc"] = strip_tags(m.group(1)) if m else ""

        m = re.search(r'<div class="sig">(.*?)</div>', c, re.S)
        card["sig"] = re.sub(r"^一皿[:：]\s*", "", strip_tags(m.group(1))) if m else ""

        card["info"] = [(strip_tags(a, False), strip_tags(b)) for a, b in
                        re.findall(r"<tr>\s*<th>(.*?)</th>\s*<td[^>]*>(.*?)</td>\s*</tr>", c, re.S)]

        m = re.search(r'<div class="reason">(.*?)</div>', c, re.S)
        card["reason"] = re.sub(r"^選定理由[:：]\s*", "", strip_tags(m.group(1))) if m else ""

        m = re.search(r'<a class="map" href="([^"]*)"', c)
        card["map"] = htmllib.unescape(m.group(1)) if m else ""

        m = re.search(r'<img class="hero"[^>]*src="([^"]+)"', c)
        card["img"] = htmllib.unescape(m.group(1)) if m else ""

        m = re.search(r'<div class="src">(.*?)</div>', c, re.S)
        if m:
            sv = strip_tags(m.group(1))
            sv = re.sub(r"^写真[:：].*?[/／]\s*参照元[:：]\s*", "", sv)
            card["src"] = re.sub(r"^参照元[:：]\s*", "", sv)
        else:
            card["src"] = ""
        out.append(card)
    return out


def render_card(c, imgdir):
    ttl = ("%s. %s" % (c["no"], c["name"])) if c["no"] else c["name"]
    if c["yomi"]:
        ttl += "（%s）" % c["yomi"]
    L = ["### " + esc(ttl), ""]
    if c["img"]:
        L += ["@@IMG:%s@@" % os.path.join(imgdir, c["img"]).replace("\\", "/"), ""]
    if c["chips"]:
        L += [" ".join("`%s`" % t for t in c["chips"]), ""]
    if c["desc"]:
        L += [esc(c["desc"]), ""]
    if c["sig"]:
        L.append("- **一皿**: " + esc(c["sig"]))
    for k, v in c["info"]:
        L.append("- **%s**: %s" % (esc(k), esc(v)))
    if c["reason"]:
        L.append("- **選定理由**: " + esc(c["reason"]))
    if c["map"]:
        L.append("- **地図**: [Googleマップで開く](%s)" % c["map"])
    if c["src"]:
        L.append("- **参照元**: " + esc(c["src"]))
    L.append("")
    return "\n".join(L)


def render_maps(body, imgdir):
    """<div class="mapsec"> の店舗マップ画像を Notion 用の節にする。

    Notion は画像内のリンク（HTML版のピン）を再現できないので、
    見出しの「（ピンをタップで各店のページへ）」は落として注記に置き換える。
    地図画像が無いガイド（欧州8冊）では空を返し、節そのものを出さない。
    """
    shots = []
    for m in re.finditer(r'<div class="mapttl">(.*?)</div>(.*?)(?=<div class="mapttl">|\Z)', body, re.S):
        ttl = strip_tags(m.group(1), False)
        img = re.search(r'<img src="([^"]+)"', m.group(2))
        if img:
            shots.append((ttl, htmllib.unescape(img.group(1))))
    if not shots:
        return []

    out = ["## 🗾 店舗マップ", ""]
    for ttl, src in shots:
        ttl = re.sub(r"[（(]ピンをタップ[^）)]*[）)]", "", ttl).strip()
        ttl = re.sub(r"^🗾\s*店舗マップ\s*[—\-–]\s*", "", ttl).strip()
        if ttl:
            out += ["**%s**" % esc(ttl), ""]
        out += ["@@IMG:%s@@" % os.path.join(imgdir, src).replace("\\", "/"), ""]

    note = re.search(r'<div class="mapnote">(.*?)</div>', body, re.S)
    tail = strip_tags(note.group(1)) if note else "地図: © OpenStreetMap contributors"
    # 「Notion版ではピンをタップできない」と書いていたが、それは製品全体の話ではなく
    # 「この画像の中では」という話だった（Notion のデータベースの地図ビューならタップできる）。
    # 主語を実装まで狭める（B-333）。
    out += ["> %s ／ この画像のピンはタップできません。各店の位置は"
            "カード内の「地図」リンク（Googleマップ）から開いてください。" % esc(tail), ""]
    return out


def convert(path, imgdir):
    s = io.open(path, encoding="utf-8").read()
    body = s.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    out = []

    cov = re.search(r'<div class="cover">(.*?)\n</div>', body, re.S)
    if cov:
        cv = cov.group(1)
        for pat in (r'<div style="font-size:8\.5pt[^"]*">(.*?)</div>', r'<div class="sub">(.*?)</div>'):
            m = re.search(pat, cv, re.S)
            if m:
                out += [esc(strip_tags(m.group(1))), ""]
        m = re.search(r'<div class="meta">(.*?)</div>', cv, re.S)
        if m:
            out += ["> " + esc(strip_tags(m.group(1))), ""]

    lg = re.search(r'<div class="legend">(.*?)</div>', body, re.S)
    if lg:
        rows = re.findall(r'<span class="chip ([^"]*)">(.*?)</span>([^<]*)', lg.group(1), re.S)
        if rows:
            out += ["**タグの意味**", ""]
            for _cls, label, desc in rows:
                out.append("- `%s` — %s" % (esc(strip_tags(label, False)),
                                            esc(re.sub(r"\s+", " ", htmllib.unescape(desc)).strip())))
            out.append("")
    out += ["> 📷 写真は各店の料理・店内の実写（Google Maps投稿写真 ©各投稿者/Google）。", ""]
    out += ["@@TOC@@", ""]
    out += render_maps(body, imgdir)
    out += ["---", ""]

    total = 0
    parts = re.split(r"<h2\b[^>]*>(.*?)</h2>", body, flags=re.S)
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            cards = parse_cards(parts[i + 1])
            total += len(cards)
            out += ["## " + esc(strip_tags(parts[i], False)), ""]
            note = re.search(r'<div class="secnote">(.*?)</div>', parts[i + 1], re.S)
            if note:
                out += [esc(strip_tags(note.group(1))), ""]
            for c in cards:
                out.append(render_card(c, imgdir))
    else:
        cards = parse_cards(body)
        total = len(cards)
        for c in cards:
            out.append(render_card(c, imgdir))

    tail = re.search(r'<p class="tiny"[^>]*>(.*?)</p>', body, re.S)
    if tail:
        out += ["---", "", "> " + esc(strip_tags(tail.group(1)))]

    title = re.search(r"<title>(.*?)</title>", s, re.S)
    return (strip_tags(title.group(1), False) if title else os.path.basename(path)), total, "\n".join(out)


def chunk(text):
    """MAX_CHUNK 以下に分割。分割点は ## / ### 見出しの直前だけ（店カードを割らない）。"""
    units, cur = [], []
    for ln in text.split("\n"):
        if re.match(r"^#{2,3} ", ln) and cur:
            units.append("\n".join(cur).rstrip("\n"))
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        units.append("\n".join(cur).rstrip("\n"))

    res, buf = [], ""
    for u in units:
        cand = (buf + "\n\n" + u) if buf else u
        if len(cand) > MAX_CHUNK and buf:
            res.append(buf)
            buf = u
        else:
            buf = cand
    if buf:
        res.append(buf)

    out = []
    for c in res:
        last = out[-1].rstrip().split("\n")[-1] if out else ""
        if out and last.startswith("## ") and len(out[-1].strip()) == len(last):
            out[-1] += "\n\n" + c
        else:
            out.append(c)
    return out


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for f in os.listdir(OUT):
        if f.endswith(".md"):
            os.remove(os.path.join(OUT, f))

    manifest, index = [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".html"):
                continue
            full = os.path.join(dirpath, fn)
            relbase = os.path.relpath(dirpath, ROOT).replace("\\", "/")   # japan/kyoto
            base = (relbase + "/" + fn[:-5]).replace("/", "_")            # japan_kyoto_kyoto
            title, total, md = convert(full, relbase)
            parts = chunk(md)
            for i, c in enumerate(parts, 1):
                name = "%s.part%02d.md" % (base, i)
                fh = io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n")
                fh.write(c)
                fh.close()
                for rel in re.findall(r"@@IMG:([^@]+)@@", c):
                    manifest.append({"guide": base, "part": name, "path": rel})
            index.append((base, title, total, len(parts)))
            print("%-34s %-26s stores=%-4d parts=%d" % (base, title[:26], total, len(parts)))

    fh = io.open(MANIFEST, "w", encoding="utf-8", newline="\n")
    fh.write(json.dumps(manifest, ensure_ascii=False, indent=1))
    fh.close()
    missing = [m for m in manifest if not os.path.isfile(os.path.join(ROOT, m["path"]))]
    print("---")
    print("guides=%d  stores=%d  parts=%d  images=%d  missing=%d"
          % (len(index), sum(x[2] for x in index), sum(x[3] for x in index),
             len(manifest), len(missing)))
    for m in missing[:10]:
        print("  MISSING", m["path"])


if __name__ == "__main__":
    main()
