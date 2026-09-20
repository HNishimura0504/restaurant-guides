# -*- coding: utf-8 -*-
"""調査で得た新しい店を、**既存の記事の様式そのままに**差し込む。

店数基準（規約 §2）＝人口50万以上 約72店／20〜50万 約50店／20万未満 約45店。
これを下回る冊に足すために使う。

**本文の他の部分には触らない。** 触るのは ①該当する章の末尾へカードを1枚足す
②表紙の店数 ③目次 の3か所だけ。地図のピンと `stores.json` は、あとで
`build_map.py` / `stores_extract.py` を回し直すことで追随する（規約 §7 [2026-08-02]）。

使い方: python3 notion/add_stores.py <記事のパス> <新しい店のJSON>
JSON の形は `docs/` の要件定義書 `requirements_rule_backfill_2026.md` §3 を参照。
"""
import io, json, os, re, sys, urllib.parse

CHIP = {"地元密着": "local", "老舗・歴史": "hist", "口コミ突出": "pop",
        "ブログ推薦": "blog", "隣接市": "near", "食の専門街": "street"}


def card(st, num, color):
    """既存のカードと**同じ並び**で組む（規約 §2「店カードの必須要素」上から順）。"""
    chips = "".join('<span class="chip %s">%s</span>' % (CHIP.get(c, "local"), c)
                    for c in st.get("chips", [])[:3])
    q = urllib.parse.quote("%s %s" % (st["name"], st["addr"]))
    src = " / ".join('<a href="%s">%s</a>' % (s["url"], s["label"]) for s in st.get("src", []))
    photo = ""
    if st.get("photo_file"):
        photo = ('\n  <img class="hero" src="img/%s/%s.jpg" alt="%s 料理・店内写真">'
                 % (st["_city"], st["sid"], st["name"]))
    else:
        # **写真が無いことを黙って隠さない。** 既存の保留の札と同じ形にする。
        photo = ('\n  <div class="hero-pending">写真準備中<span>'
                 '規約に合う写真が見つからなかった</span></div>')
    psrc = ""
    if st.get("photo_src_page"):
        h = urllib.parse.urlparse(st["photo_src_page"]).netloc.replace("www.", "")
        psrc = '写真: <a href="%s">%s</a> / ' % (st["photo_src_page"].replace("&", "&amp;"), h)
    return """<div class="card" id="c-%(sid)s">%(photo)s
  <div class="body">
    <div class="nm"><span class="pinno" style="background:%(color)s;">%(num)d</span>%(name)s<span class="yomi">%(yomi)s</span></div>
    <div class="chips">%(chips)s</div>
    <div class="desc">%(desc)s</div>
    <div class="sig"><b>一皿:</b>%(sig)s</div>
    <table class="info">
      <tr><th>営業時間</th><td>%(hours)s</td></tr>
      <tr><th>定休日</th><td class="off">%(closed)s</td></tr>
      <tr><th>住所</th><td>%(addr)s</td></tr>
      <tr><th>予約</th><td>%(reserve)s</td></tr>
    </table>
    <div class="reason"><b>選定理由:</b>%(reason)s</div>
    <a class="map" href="https://www.google.com/maps/search/?api=1&amp;query=%(q)s">Googleマップで開く</a>
    <div class="src">%(psrc)s参照元: %(src)s</div>
  </div></div>""" % dict(st, photo=photo, chips=chips, q=q, src=src, psrc=psrc,
                         num=num, color=color)


def main():
    path, js = sys.argv[1], sys.argv[2]
    s = io.open(path, encoding="utf-8").read()
    city = os.path.basename(path)[:-5]
    new = json.load(io.open(js, encoding="utf-8"))
    for st in new:
        st["_city"] = city

    # 章の見出し（`<h2 id="s-…">`）を出現順に拾い、章名 → id の対応を作る
    heads = [(m.group(1), re.sub("<[^>]+>", "", m.group(2)).strip(), m.end())
             for m in re.finditer(r'<h2[^>]*id="(s-[^"]+)"[^>]*>(.*?)</h2>', s, re.S)]
    if not heads:
        sys.exit("章の見出しが見つからない")

    added = 0
    for st in new:
        tgt = None
        for hid, label, _ in heads:
            if st["chapter"] in label or label in st["chapter"]:
                tgt = hid
                break
        if not tgt:
            print("   章が合わない: %s（%s）" % (st["sid"], st["chapter"]))
            continue
        if '<div class="card" id="c-%s">' % st["sid"] in s:
            print("   既に在る: %s" % st["sid"])
            continue
        # その章の**最後のカードの直後**へ入れる（次の h2 の手前まで）
        i = s.index('id="%s"' % tgt)
        nxt = re.search(r'<h2[^>]*id="s-', s[i + 10:])
        end = i + 10 + nxt.start() if nxt else len(s)
        last = s.rindex("</div></div>", i, end) + len("</div></div>")
        color = re.search(r'<span class="pinno" style="background:([^;]+);',
                          s[i:end])
        color = color.group(1) if color else "#2a78d6"
        s = s[:last] + "\n" + card(st, 0, color) + s[last:]
        added += 1

    # 通し番号を**本文の出現順で振り直す**（ピンの番号と合わせるため）
    n = 0
    out = []
    for part in re.split(r'(<span class="pinno" style="background:[^;]+;">\d*</span>)', s):
        m = re.match(r'(<span class="pinno" style="background:[^;]+;">)\d*(</span>)', part)
        if m:
            n += 1
            out.append("%s%d%s" % (m.group(1), n, m.group(2)))
        else:
            out.append(part)
    s = "".join(out)

    # 表紙の店数を直す
    total = s.count('<div class="card" id="c-')
    s = re.sub(r"(\d+)\s*店", lambda m: "%d店" % total, s, count=1)
    io.open(path, "w", encoding="utf-8").write(s)
    print("%-40s 足した %d 店 / 合計 %d 店（番号を振り直した）" % (path, added, total))
    print("   このあと build_map.py → stores_extract.py の順で回し直すこと（地図と目次が追随する）")


if __name__ == "__main__":
    main()
