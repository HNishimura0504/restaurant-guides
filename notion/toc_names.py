# -*- coding: utf-8 -*-
"""目次の見出しを「一言紹介」から「店名」に変え、一言は小さい灰色の副題にする。

ユーザー依頼（2026-09-21）「**目次の名前が各店舗の一言紹介になってる。店名にしてくれ。
でも一言コメントもあると嬉しいから点目にの下に小さく灰色で付け足してくれ**」
（「点目に」は「店名」の打ち間違いと読む）。

**実測した現状**: 目次の各行は `<a href="#c-…"><span class="tn">1</span>明治二年創業の鮒寿し老舗</a>` で、
**店名（元祖阪本屋）がどこにも出ていない。** ピンの番号と一言だけなので、
「あの店はどこ？」という引き方ができない。

**なぜ地図ごと作り直さないか**: `add_guide_map.py --rebuild` は目次と一緒に**地図のPNGも作り直す**
（OSM のタイルを取り直す）。今回変えたいのは目次の1行の中身だけなので、
**本文にも地図にも触らず、目次のアンカーの中身だけを差し替える**。

**一言はどこから来るか**: `stores.json` に一言の欄は無い。**いま目次に書かれている文言が唯一の出所**なので、
**それを拾って副題へ移す**（消さない）。店名は `stores.json` の `店名` を正とする。

**冪等**: 既に `class="tsub"` を持つ目次は飛ばす。

使い方:  python3 notion/toc_names.py [--dry-run]
"""
import io
import json
import os
import re
import sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
MARK = 'id="tocname"'

CSS = """<style id="tocname">
/* 目次の1行を「番号＋店名」＋その下に小さい灰色の一言、の2段にする（2026-09-21 依頼）。
   副題は番号バッジ（min-width 4.6mm ＋ 右余白 1.2mm）のぶんだけ字下げして、店名の頭に揃える。 */
.toc a{line-height:1.3;}
.toc a .tnm{font-weight:600;}
.toc a .tsub{display:block; margin-left:5.8mm; margin-top:.2mm;
  font-size:7.4pt; font-weight:400; color:var(--ink3); line-height:1.25;}
/* 既存の `.toc a::after{content:" ›"}` はアンカーの末尾に付くので、副題を足すと
   **3行目に矢印だけが残る**（実測）。矢印は店名の後ろへ移す。 */
.toc a::after{content:none;}
.toc a .tnm::after{content:" \203A"; color:var(--ink3); font-weight:400;}
</style>
"""

A = re.compile(r'(<a href="#(c-[^"]+)">)(<span class="tn"[^>]*>\d+</span>)?(.*?)(</a>)', re.S)


def main():
    dry = "--dry-run" in sys.argv
    stores = json.load(io.open(STORES, encoding="utf-8"))
    name = {}
    for r in stores:
        if r.get("slug") and r.get("path"):
            name.setdefault(r["path"], {})["c-" + r["slug"]] = r["店名"]

    done = skipped = rows = same = 0
    for path in sorted(name):
        full = os.path.join(ROOT, path)
        s = io.open(full, encoding="utf-8").read()
        if MARK in s:
            skipped += 1
            continue
        nm = name[path]
        cnt = [0, 0]

        def rep(m):
            open_a, sid, badge, text, close = m.groups()
            if 'class="tsub"' in text:          # 既に2段になっている
                return m.group(0)
            n = nm.get(sid)
            if not n:
                return m.group(0)
            sub = re.sub(r"<[^>]+>", "", text).strip()
            cnt[0] += 1
            if not sub or sub == n:
                cnt[1] += 1
                return "%s%s<span class=\"tnm\">%s</span>%s" % (open_a, badge or "", escape(n), close)
            return ("%s%s<span class=\"tnm\">%s</span><span class=\"tsub\">%s</span>%s"
                    % (open_a, badge or "", escape(n), escape(sub), close))

        s2 = A.sub(rep, s)
        if cnt[0] == 0:
            print("   ! 目次の行が見つからない:", path)
            continue
        s2 = s2.replace("</head>", CSS + "</head>", 1)
        if not dry:
            io.open(full, "w", encoding="utf-8", newline="\n").write(s2)
        rows += cnt[0]
        same += cnt[1]
        done += 1

    print("直した記事: %d / 既に2段: %d / 目次の行 %d（うち一言が無い・店名と同じ %d）%s"
          % (done, skipped, rows, same, "（--dry-run なので書いていない）" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
