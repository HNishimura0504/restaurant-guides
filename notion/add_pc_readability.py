# -*- coding: utf-8 -*-
"""ガイド記事を、PCの広い画面でも読める版面にする（画面用のみ・紙面は不変）。

ユーザー指摘（2026-09-21）「**さすがにPCで見た時の一覧の料理の画像がでかすぎるな。
むかしwebページの設計思想やデザインノウハウについてweb調査してもらったと思うけど、
それを活かせないの？**」

**実測した不具合**（変更前・ヘッドレス Chromium）:

| 画面幅 | 本文の1行 | 料理写真 |
|---|---|---|
| 1280px | **全角 約99字** | **1278 x 257px**（縦横比 5:1） |
| 1920px | **全角 約149字** | **1918 x 257px**（縦横比 7.5:1） |
| 390px | 全角 約24字 | 388 x 257px |

**根拠（エビデンスの高い順）**:

1. **W3C / WCAG 2.2 達成基準 1.4.8 Visual Presentation（レベル AAA）**
   — 「Width is no more than 80 characters or glyphs (**40 if CJK**)」。
   日本語は**全角40字**が上限。https://www.w3.org/WAI/WCAG21/Understanding/visual-presentation.html
2. **タイポグラフィの古典と読字研究** — Bringhurst の 45〜75 字（欧文）、
   Dyson & Haselgrove の実験で **約55字/行**が速読・通常読のどちらでも成績がよい。
   https://baymard.com/blog/line-length-readability
3. 実務のまとめ（企業）— 50〜75字、66字が目安。https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/

**＝1280px で99字は上限40字の2.5倍。写真が大きすぎるのは症状で、原因は
「本文の段に上限が無く、窓幅いっぱいに伸びること」。段に上限を付ければ写真も一緒に収まる。**

**直し方（2つだけ）**:

- `body` に **段の上限**と中央寄せ。上限は「全角40字」から逆算する（下の `COL_PX`）。
- `.hero` の高さ 68mm 固定をやめ、**`aspect-ratio` で紙面と同じ比（105.5:68）を保つ**。
  高さを固定したまま幅だけ広がると、640x853 の写真が 5:1 に切り取られて何が写っているか分からなくなる。
  `aspect-ratio` は MDN 記載の標準プロパティ。https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio

**紙面には触らない**: 規則はすべて `@media screen` の中。`@page{size:120mm 240mm}` と
既存の印刷用の指定は1つも変えない。

**スマホには影響しない**: 上限 `COL_PX` は 390px より広いので、狭い画面では何も起きない。

**冪等**: 既に入っている記事は飛ばす。`--force` で入れ直す。

使い方:  python3 notion/add_pc_readability.py [--dry-run] [--force]
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
MARK = 'id="pcread"'

# 段の上限（px）。本文 `.desc` の実測サイズ × 全角40字 ＋ カード左右の余白から逆算する。
# 数値の決め方は docstring の根拠1（WCAG 1.4.8 の CJK 40字）に従う。
# 本文 `.desc` は 9.5pt＝12.67px。全角40字 ＝ 12.67 x 40 ≒ 507px に、
# カード左右の余白（4mm x 2 ≒ 30px）を足して 540px。
COL_PX = 540
# **1行の字数は「段の幅 ÷ 文字の大きさ」でしか決まらない**ので、字を大きくしても字数は減らない。
# 字数は上の COL_PX で合わせ、**読みやすさ（文字の見かけの大きさ）は `zoom` で別に上げる**。
# `zoom` は CSS Viewport モジュールの標準プロパティで、主要ブラウザが対応している。
# https://developer.mozilla.org/en-US/docs/Web/CSS/zoom
ZOOM = 1.2

BLOCK = """<style id="pcread">
/* --- PCの広い画面向け（画面のみ・紙面は不変） -------------------------------
   WCAG 2.2 達成基準 1.4.8（AAA）＝日本語は**全角40字**が1行の上限。
   変更前の実測は 1280px で約99字・1920px で約149字だった。
   段に上限を付けると、幅いっぱいに伸びていた写真も一緒に収まる。
   字の見かけの大きさは `zoom` で別に上げる（字数は段の幅と字の大きさの比でしか決まらないので、
   `zoom` では字数は変わらない＝両方を別々に決められる）。 */
/* 段の上限と `zoom` は**広い画面だけ**に当てる。スマホ（幅 640px 以下、または
   「スマホ表示に固定」）には 2026-09-19 に調整した別の規則が既に当たっており、
   そこへ `zoom` を重ねると字が大きくなりすぎる（実測＝390px で 11.5pt が実質 13.8pt）。 */
@media screen and (min-width:700px){
  html:not(.vm-phone) body{max-width:%(col)dpx; margin-left:auto; margin-right:auto; zoom:%(zoom)s;}
}
@media screen{
  /* 高さ固定のままだと、窓が広いほど写真が横長に切り取られる（1280px で 5:1）。
     紙面と同じ比を保たせる。 */
  .hero{height:auto; aspect-ratio:105.5 / 68;}
  .hero-pending{height:auto; aspect-ratio:105.5 / 40;}
  /* 地図と目次も段の中に収まる。地図は紙面と同じ比を保つ。 */
  .mapwrap img,.mapsec img{height:auto;}
}
</style>
""" % {"col": COL_PX, "zoom": ("%g" % ZOOM)}


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    stores = json.load(io.open(STORES, encoding="utf-8"))
    paths = sorted({r["path"] for r in stores if r.get("path")})

    done = skipped = 0
    for path in paths:
        full = os.path.join(ROOT, path)
        s = io.open(full, encoding="utf-8").read()
        if MARK in s:
            if not force:
                skipped += 1
                continue
            i = s.index('<style id="pcread">')
            j = s.index("</style>\n", i) + len("</style>\n")
            s = s[:i] + s[j:]
        if "</head>" not in s:
            print("   ! </head> が無い:", path)
            continue
        # 既存の <style> より後ろへ置く（同じ詳細度なら後ろが勝つ）。
        s = s.replace("</head>", BLOCK + "</head>", 1)
        if not dry:
            io.open(full, "w", encoding="utf-8", newline="\n").write(s)
        done += 1

    print("入れた: %d / 既にあった: %d / 合計 %d 本%s"
          % (done, skipped, len(paths), "（--dry-run なので書いていない）" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
