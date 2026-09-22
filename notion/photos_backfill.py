# -*- coding: utf-8 -*-
"""「写真準備中」の店に、2巡目で集めた写真を後から入れる。

ユーザー指示（2026-09-20）「**公式HPや個人ブログなどから可能な限り外観写真を引用する**」。

**なぜ後入れが要るか**: 1巡目は各店の公式サイトだけを見たため、
①JS の遅延読み込みで HTML から画像URLが取れない ②Cloudflare で弾かれる
③公式サイトが無く SNS だけ、の3つで落ちた店が5冊で85店あった。
2巡目で**公式観光サイト・地域メディア・個人ブログ**まで広げて拾い直した結果を、
**記事を作り直さずに** `<div class="hero-pending">…</div>` と差し替える。

**料理・店内が取れず外観しか無い店**は、外観を使い、
`写真:` の欄に**外観であることを明記**する（黙って料理写真のように見せない）。

**冪等**: 既に `<img class="hero">` を持つ店は触らない。

使い方:
  python3 notion/photos_backfill.py <picks.json> <記事のパス> <city>

picks.json の形:
  {"<sid>": {"file": "/絶対パス/3.jpg", "src": "Visit Luxembourg の店舗ページ"} , ...}
"""
import io
import json
import os
import re
import shutil
import sys
from html import escape


def main():
    picks_path, page, city = sys.argv[1], sys.argv[2], sys.argv[3]
    picks = json.load(io.open(picks_path, encoding="utf-8"))
    s = io.open(page, encoding="utf-8").read()
    d = os.path.dirname(page)
    imgdir = os.path.join(d, "img", city)
    os.makedirs(imgdir, exist_ok=True)

    done = skip = 0
    for sid, v in picks.items():
        # そのカードの範囲だけを見る（別の店の hero を書き換えないため）
        m = re.search(r'(<div class="card" id="c-%s">)(.*?)(</div>\s*</div>)'
                      % re.escape(sid), s, re.S)
        if not m:
            print("   ! カードが無い:", sid)
            continue
        card = m.group(2)
        if '<img class="hero"' in card:
            skip += 1
            continue
        if 'class="hero-pending"' not in card:
            print("   ! 準備中でもない:", sid)
            continue
        shutil.copy(v["file"], os.path.join(imgdir, sid + ".jpg"))
        alt = "%s 料理・店内写真" % sid
        new_card = re.sub(r'<div class="hero-pending">.*?</div>\s*',
                          '<img class="hero" src="img/%s/%s.jpg" alt="%s">\n'
                          % (city, sid, escape(alt)), card, count=1, flags=re.S)
        # 出典の行を差し替える（「写真: 準備中」→ 実際の出どころ）
        new_card = new_card.replace('写真: 準備中', '写真: %s' % escape(v["src"]), 1)
        s = s[:m.start(2)] + new_card + s[m.end(2):]
        done += 1

    io.open(page, "w", encoding="utf-8", newline="\n").write(s)
    print("%-38s 入れた %2d / 既にあった %2d / 残る準備中 %2d"
          % (page, done, skip, s.count('class="hero-pending"')))
    return 0


if __name__ == "__main__":
    sys.exit(main())
