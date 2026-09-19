# -*- coding: utf-8 -*-
"""ガイド記事66本を、スマホでも実寸で読めるようにする（＋表示モードの切替）。

ユーザー依頼（2026-09-19）「**閲覧してるデバイスがpc/タブレットかスマホかを判別して、
pc/タブレットモードとスマホモード2パターンで表示されるようにできる？**」
要件＝`docs/requirements_responsive_2026.md`（方式は本人が「レスポンシブ＋手動切替」を選択）。

**直している実害（実測）**: 66本すべてに **`<meta name="viewport">` が無い**。
その場合スマホのブラウザは **仮想的に 980px の画面として描画し、実機幅に合わせて縮小する**
（390/980 ＝ **40%**）。本文 10.5pt が実質 4pt になり、**拡大しないと読めない**。
**`viewport` の1行を足すだけで縮小が止まる**のが、この変更の中心。

**各記事のCSSに依存しない**: 66本はそれぞれ独立した `<style>` を持ち、クラス名の集合は6通りに
分かれる（実測）。**共通して存在するクラスだけに当てる**＝`.toc .links`（目次の2段組み・66本）・
`.cover` `.desc` `.chip` `.info th`（いずれも66本）。無い記事では単に何も起きない。

**紙面の体裁は触らない**: 66本とも `@page{size:120mm 240mm}` を持つ。
足す規則は**すべて画面用**（`@media print` の外）で、`@page` には一切触れない。

**冪等**: 既に入っている記事は飛ばす。ガイドを追加したら、このスクリプトをもう一度走らせる。

使い方:  python3 notion/add_responsive.py [--dry-run]
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rwd import TOGGLE_CSS, TOGGLE_HTML, TOGGLE_JS, dual   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
MARK = 'id="rwd"'
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'

# スマホで当てる規則。`@@` は rwd.dual() が2通りの前置きへ展開する。
MOBILE = """
@@ body{font-size:11.5pt}
@@ .cover{padding:5mm 4.5mm}
@@ .cover h1{font-size:15pt}
@@ .legend{font-size:10pt;padding:3mm}
@@ .toc .links{grid-template-columns:1fr}
@@ .toc .sec{font-size:10pt}
@@ .toc .links > *{font-size:10pt;padding:.8mm 0}
@@ .desc{font-size:11pt}
@@ .reason,@@ .src{font-size:9.5pt}
@@ .chip{font-size:9pt;padding:.6mm 3mm}
@@ .info th{width:auto;white-space:normal}
@@ .gnav{font-size:11pt;gap:10px}
"""

BLOCK = """<style id="rwd">
%(mobile)s%(toggle)s</style>
""" % {"mobile": dual(MOBILE), "toggle": TOGGLE_CSS}

SCRIPT = "<script>%s</script>\n" % TOGGLE_JS


def main():
    dry = "--dry-run" in sys.argv
    stores = json.load(io.open(STORES, encoding="utf-8"))
    paths = sorted({r["path"] for r in stores if r.get("path")})

    done = skipped = 0
    for path in paths:
        full = os.path.join(ROOT, path)
        s = io.open(full, encoding="utf-8").read()
        if MARK in s:
            skipped += 1
            continue

        # ① viewport メタ。<head> の先頭寄り（charset の直後）へ。
        if 'name="viewport"' not in s:
            if "<meta charset" in s:
                i = s.index("<meta charset")
                j = s.index(">", i) + 1
                s = s[:j] + "\n" + VIEWPORT + s[j:]
            else:
                s = s.replace("<head>", "<head>\n" + VIEWPORT, 1)

        # ② スマホ用の規則と切替の見た目。既存の <style> の後ろに置いて上書きできるようにする。
        s = s.replace("</head>", BLOCK + "</head>", 1)

        # ③ 切替ボタンを行き来の帯（gnav）の中へ。無い記事では <body> 直後に置く。
        # **有無の判定に `vmsw` を使わない**＝②で差し込んだCSSにも `.vmsw` が入っているので、
        # 素朴に `"vmsw" not in s` と書くと**必ず偽になり、ボタンが一度も入らない**（実測で踏んだ）。
        # 判定はボタンの literal そのもので行う。
        if '<div class="gnav">' in s and TOGGLE_HTML not in s:
            i = s.index('<div class="gnav">')
            j = s.index(">", i) + 1
            s = s[:j] + "\n  " + TOGGLE_HTML + s[j:]
        elif TOGGLE_HTML not in s:
            s = s.replace("<body>", '<body>\n<div class="gnav">%s</div>' % TOGGLE_HTML, 1)

        # ④ 切替の本体は </body> の直前（要素が出来てから動かす）。
        s = s.replace("</body>", SCRIPT + "</body>", 1)

        if not dry:
            io.open(full, "w", encoding="utf-8", newline="\n").write(s)
        done += 1

    print("足した: %d / 既にあった: %d / 合計 %d 本%s"
          % (done, skipped, len(paths), "（--dry-run なので書いていない）" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
