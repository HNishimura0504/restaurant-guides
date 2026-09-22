#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""見出し写真（hero）の解像度不足を検出する。

記事の本文カラムは PC で 540 CSS px（WCAG 2.2 SC 1.4.8 の全角40字に合わせた幅）、
`zoom:1.2` が掛かるのでデバイス画素では 648px。カード左右の余白 4mm x 2 ≒ 30px を
引いた 612px が hero の実表示幅で、比率は 105.5:68。
つまり hero は 612 x 394 px で描かれる。元画像がこれより小さいと拡大されてボケる。

この検査は「拡大率 = max(612/w, 394/h)」を計算し、しきい値を超えた画像を挙げる。
写真を集める時点でこの下限（長辺 900px 以上を推奨）を条件に入れること。
2026-09-22 に 55 枚の不足が後から見つかったのは、1巡目の選定に大きさの条件が
無かったため。

使い方:
    python3 notion/check_hero_size.py [--max-upscale 1.5] [--json out.json]
"""
import argparse
import json
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow が要る: pip install pillow")

BOX_W = 612.0
BOX_H = BOX_W / (105.5 / 68.0)

HERO = re.compile(r'<img class="hero" src="(img/[^"]+)"[^>]*alt="([^"]*)"')


def guides(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "notion", "docs", "map")]
        for fn in filenames:
            if fn.endswith(".html") and fn != "index.html":
                yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--max-upscale", type=float, default=1.5)
    ap.add_argument("--json")
    a = ap.parse_args()

    bad, total = [], 0
    for path in sorted(guides(a.root)):
        s = open(path, encoding="utf-8").read()
        for rel, alt in HERO.findall(s):
            img = os.path.join(os.path.dirname(path), rel)
            if not os.path.exists(img):
                bad.append(dict(path=os.path.relpath(path, a.root), img=rel,
                                w=0, h=0, up=99.0, alt=alt, note="ファイルが無い"))
                continue
            total += 1
            with Image.open(img) as im:
                w, h = im.size
            up = max(BOX_W / w, BOX_H / h)
            if up > a.max_upscale:
                bad.append(dict(path=os.path.relpath(path, a.root), img=rel,
                                w=w, h=h, up=round(up, 2), alt=alt))

    bad.sort(key=lambda x: -x["up"])
    for x in bad:
        print("%5.2fx %-46s %4dx%-4d %s" % (x["up"], x["img"], x["w"], x["h"], x["alt"][:30]))
    print("hero %d 枚中 %d 枚が拡大率 %.2f 超" % (total, len(bad), a.max_upscale))
    if a.json:
        json.dump(bad, open(a.json, "w"), ensure_ascii=False, indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
