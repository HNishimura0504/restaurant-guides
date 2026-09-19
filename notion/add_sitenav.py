# -*- coding: utf-8 -*-
"""ガイド記事の先頭に「この都市の地図」「都市一覧」への行き来を足す。

ユーザー依頼（2026-09-19）「**リンクを送れよ。他のガイドも全部に適応してくれ**」。

**なぜ要るか**: 地図ページ（`map/<都市>.html`）からは記事の該当店へ飛べるのに、
**記事側から地図へ戻る道が1本も無かった**（実測＝66本のガイドのうち、
`map/` を含む9本はいずれも外部サイトの URL に `map/` が入っていただけで、
自分の地図ページを指す `href` は**0本**）。記事を開いた人は、地図が在ることに気づけない。

**なぜ各記事のCSSに依存しないか**: 66本のガイドはそれぞれ独立した `<style>` を持ち、
クラス名も揃っていない。**この1行のためだけに全記事のCSSを揃えるのは割に合わない**ので、
**自前の `<style>` を同時に差し込み、クラス名も `gnav` 1つに閉じる**。

**印刷では消す**: ガイドは `@page{size:120mm 240mm}` を持つ**紙面向けの体裁**なので、
画面用の行き来は `@media print` で隠す。

**冪等**: 既に入っている記事は飛ばす。ガイドを追加したら、このスクリプトをもう一度走らせる。

使い方:  python3 notion/add_sitenav.py [--dry-run]
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
MARK = 'class="gnav"'

BLOCK = """<style>
.gnav{display:flex;gap:14px;align-items:center;flex-wrap:wrap;
      padding:8px 12px;margin:0 0 10px;border-bottom:1px solid #e4e2dc;
      font-size:9.5pt;font-family:system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
.gnav a{color:#8a2b16;text-decoration:none}
.gnav a:hover{text-decoration:underline}
.gnav span{color:#8a8880}
@media print{.gnav{display:none}}
</style>
<div class="gnav">
  <a href="../../map/%(slug)s.html">🗺️ %(city)sの地図で見る</a>
  <a href="../../index.html">📖 全%(n)d都市の一覧</a>
  <span>%(count)d店</span>
</div>
"""


def main():
    dry = "--dry-run" in sys.argv
    stores = json.load(io.open(STORES, encoding="utf-8"))

    cities = {}
    for r in stores:
        p = r.get("path")
        if not p:
            continue
        c = cities.setdefault(p, {"city": r.get("都市") or "", "n": 0})
        c["n"] += 1

    done = skipped = 0
    for path, meta in sorted(cities.items()):
        full = os.path.join(ROOT, path)
        s = io.open(full, encoding="utf-8").read()
        if MARK in s:
            skipped += 1
            continue
        if "<body>" not in s:
            print("   ! <body> が無い:", path)
            continue
        slug = os.path.basename(path)[:-5]
        block = BLOCK % {"slug": slug, "city": meta["city"],
                         "n": len(cities), "count": meta["n"]}
        s = s.replace("<body>", "<body>\n" + block, 1)
        if not dry:
            io.open(full, "w", encoding="utf-8", newline="\n").write(s)
        done += 1

    print("足した: %d / 既にあった: %d / 合計 %d 本%s"
          % (done, skipped, len(cities), "（--dry-run なので書いていない）" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
