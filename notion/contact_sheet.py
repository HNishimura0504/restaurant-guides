# -*- coding: utf-8 -*-
"""外観写真のコンタクトシート（一覧画像）を作る。目視確認を現実的な枚数に減らすため。

射程: `*_exterior.jpg` のみ。料理写真は対象外。
使い方: python3 notion/contact_sheet.py <出力先ディレクトリ> [都市...]
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS, ROWS = 4, 5          # 1枚あたり20店
TW, TH = 320, 200          # 縮小後の1コマ
LABEL = 22


def main():
    outdir = sys.argv[1]
    cities = sys.argv[2:] or ["大阪", "京都", "吹田", "東京23区", "ルーベン"]
    stores = json.load(open(os.path.join(ROOT, "notion", "stores.json"),
                            encoding="utf-8"))
    idx = {"%s/%s" % (s["guide"], s["slug"]): s for s in stores
           if s.get("都市") in cities}
    items = []
    for k, s in sorted(idx.items()):
        p = s["guide"].split("_")
        f = os.path.join(ROOT, p[0], p[1], "img", p[2],
                         s["slug"] + "_exterior.jpg")
        if os.path.exists(f):
            items.append((f, s))
    os.makedirs(outdir, exist_ok=True)
    per = COLS * ROWS
    sheets = []
    for n in range(0, len(items), per):
        chunk = items[n:n + per]
        sheet = Image.new("RGB", (COLS * TW, ROWS * (TH + LABEL)), "white")
        d = ImageDraw.Draw(sheet)
        for j, (f, s) in enumerate(chunk):
            im = Image.open(f).convert("RGB").resize((TW, TH))
            x, y = (j % COLS) * TW, (j // COLS) * (TH + LABEL)
            sheet.paste(im, (x, y))
            d.rectangle([x, y + TH, x + TW, y + TH + LABEL], fill="white")
            d.text((x + 3, y + TH + 5),
                   "%d %s" % (n + j + 1, s["店名"][:26]), fill="black")
        out = os.path.join(outdir, "sheet_%02d.jpg" % (n // per + 1))
        sheet.save(out, quality=80)
        sheets.append(out)
        print(out, "→", len(chunk), "店")
    # 番号と店名の対応表も出す（目視で見つけた不良を指定しやすくするため）
    with open(os.path.join(outdir, "index.tsv"), "w", encoding="utf-8") as fh:
        for i, (f, s) in enumerate(items, 1):
            fh.write("%d\t%s\t%s\t%s\n" % (i, s["都市"], s["店名"], f))
    print("計 %d 枚 / %d 店" % (len(sheets), len(items)))


if __name__ == "__main__":
    main()
