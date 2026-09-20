# -*- coding: utf-8 -*-
"""ガイド記事の先頭に「上に貼りつく案内バー ＋ ☰ メニュー」を入れる。

ユーザー依頼:
  2026-09-19「**リンクを送れよ。他のガイドも全部に適応してくれ**」
             → 記事から地図へ戻る道が**0本**だったので `.gnav`（平文リンク1行）を入れた。
  2026-09-20「**地図から一覧に遷移することはできるけど、一覧ページから地図ページに
             遷移することができないからページ先頭にそのボタンを作って。
             それから|||みたいな、メニュー出すものがあるともっと使いやすいかも**」
             → `.gnav` は `position:static` なので**先頭に戻らないと使えない**。
             記事は1本3000行を超える（実測）ため、下まで読むと地図へ戻る道が消える。
             **貼りつくバー（`.snav`）へ置き換える**のがこの版。

**メニューの中身に章を入れる理由**: 記事の章は `<h2 id="s-…">` で、**全66本に共通してある**
（`add_guide_map.py` が作る目次も同じ id を指す）。目次は記事の中ほどに何枚もあるので、
**どこまで読んでいても章へ飛べる入口**が ☰ の中にあると、長い記事を往復できる。

**各記事のCSSに依存しない**: 66本はそれぞれ独立した `<style>` を持ち、クラス名も揃っていない。
バーのCSSは `sitenav.py` に閉じ、クラス名は `snav` / `sn-*` だけを使う（既存の
`.toc` `.links` `.cover` `.chip` `.info` と当たらないことを確認済み）。

**冪等**: 既に新しいバーが入っている記事は飛ばす。`--force` で入れ直す（古い `.gnav` も消す）。

使い方:  python3 notion/add_sitenav.py [--dry-run] [--force]
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rwd import TOGGLE_CSS, TOGGLE_HTML, TOGGLE_JS   # noqa: E402
from sitenav import NAV_CSS, NAV_JS, nav_html        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
MARK = 'class="snav"'

# 旧版（2026-09-19 の平文リンク1行）。置き換えるので、まとめて消せるように形を覚えておく。
OLD = re.compile(r'<style>\s*\.gnav\{.*?</style>\s*<div class="gnav">.*?</div>\s*',
                 re.S)

H2 = re.compile(r'<h2 id="(s-[^"]+)"[^>]*>(.*?)</h2>', re.S)
TAG = re.compile(r"<[^>]+>")


def block(slug, city, nc, count, chapters, has_toggle):
    """バー1枚ぶんのHTML。

    `has_toggle` は「切替（`.vmsw`）の見た目と本体が既にこの記事に入っているか」。
    **入っているのに重ねて入れると、`TOGGLE_JS` の click の購読が2本になり、
    1回押すと2段進む**（自動→PC のように1つ飛ばしになる）。ボタンの markup だけは
    メニューの中に必ず置く（旧 `.gnav` ごと消えるため）。
    """
    rows = [("この記事", None, "")]
    rows.append(("🗺️", "%sの地図で見る" % city, "../../map/%s.html" % slug))
    rows.append(("⬆", "記事の先頭へ", "#"))
    if chapters:
        rows.append(("章へ移動", None, ""))
        for cid, title in chapters:
            rows.append(("・", title, "#" + cid))
    rows.append(("ほかの都市", None, ""))
    rows.append(("📖", "全%d都市の一覧" % nc, "../../index.html"))
    rows.append(("🗺️", "全%d都市の地図" % nc, "../../map/index.html"))
    rows.append(("表示", None, ""))
    rows.append(("", "", TOGGLE_HTML))
    buttons = ['<a class="sn-btn" href="../../map/%s.html">🗺️ 地図</a>' % slug,
               '<a class="sn-btn" href="../../index.html">📖 一覧</a>']
    return ("<style>%s%s</style>\n%s\n<script>%s%s</script>\n"
            % (NAV_CSS, "" if has_toggle else TOGGLE_CSS,
               nav_html("%s美食ガイド" % city, "%d店" % count, buttons, rows,
                        "%sガイド メニュー" % city),
               NAV_JS, "" if has_toggle else TOGGLE_JS))


def chapters_of(s):
    out = []
    for cid, raw in H2.findall(s):
        t = TAG.sub("", raw).strip()
        if t:
            out.append((cid, t))
    return out


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv
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
        if MARK in s and not force:
            skipped += 1
            continue
        if "<body>" not in s:
            print("   ! <body> が無い:", path)
            continue
        # 旧 `.gnav` と、入れ直しのときは自分が前に入れたバーを外す。
        s = OLD.sub("", s)
        if MARK in s:
            i = s.index('<style>\n.snav{')
            j = s.index("</script>\n", i) + len("</script>\n")
            s = s[:i] + s[j:]
        slug = os.path.basename(path)[:-5]
        has_toggle = ("rg-view-mode" in s and ".vmsw{display:inline-flex" in s)
        s = s.replace("<body>",
                      "<body>\n" + block(slug, meta["city"], len(cities),
                                         meta["n"], chapters_of(s), has_toggle), 1)
        if not dry:
            io.open(full, "w", encoding="utf-8", newline="\n").write(s)
        done += 1

    print("入れた: %d / 既にあった: %d / 合計 %d 本%s"
          % (done, skipped, len(cities), "（--dry-run なので書いていない）" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
