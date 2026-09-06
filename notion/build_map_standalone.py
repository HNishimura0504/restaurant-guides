# -*- coding: utf-8 -*-
"""都市ごとの「1ファイルで完結する」地図を作る（チャットで送る用）。

なぜこれが要るか:
  `restaurant-guides` は**非公開リポジトリ**なので、GitHub Pages も raw.githack も使えず、
  Notion の埋め込みに要る公開URLが作れない（`blocked_routes.md` BR-024）。
  ユーザーの選択は「自己完結のファイルを送る」。写真も地図の部品も1つの HTML に埋め込むので、
  ファイルをダブルクリックするだけで開く。公開の場に何も置かない。

含めるもの:
  - Leaflet 本体（notion/vendor/）を HTML に直接書き込む
  - 各店の料理写真と外観写真を **380px・品質60 に縮めて data URI で埋め込む**
    （原寸のままだと1都市で20MB超になり、チャットで送れない）
  - 地図のタイルだけは表示時にインターネットから取る（OpenStreetMap）

使い方: python3 notion/build_map_standalone.py <出力先ディレクトリ>
"""
import base64
import io
import json
import os
import sys
from html import escape

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_map as BM  # 色・カテゴリ・都市の定義を1か所に保つ

ROOT = BM.ROOT
THUMB_W = 380
QUALITY = 60


def data_uri(rel):
    """写真を縮めて data URI にする。原寸のままだと送れない大きさになる。"""
    im = Image.open(os.path.join(ROOT, rel)).convert("RGB")
    if im.width > THUMB_W:
        im = im.resize((THUMB_W, int(im.height * THUMB_W / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=QUALITY, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def build(city, stores, outdir):
    sub = [s for s in stores if s.get("都市") == city and "lat" in s]
    data = []
    for s in sub:
        fam, gly = BM.CATEGORY.get(s["カテゴリ"], ("カフェ・酒場", "•"))
        food, ext = BM.img_paths(s)
        data.append({
            "n": s["店名"], "c": s["カテゴリ"], "f": fam, "g": gly,
            "lat": s["lat"], "lng": s["lng"],
            "d": s.get("一皿") or "", "m": s.get("Googleマップ") or "",
            "food": data_uri(food) if food else "",
            "ext": data_uri(ext) if ext else "",
        })
    css = open(os.path.join(ROOT, "notion", "vendor", "leaflet.css"), encoding="utf-8").read()
    js = open(os.path.join(ROOT, "notion", "vendor", "leaflet.js"), encoding="utf-8").read()
    page = BM.city_page(city, sub)
    page = page.replace('<link rel="stylesheet" href="vendor/leaflet.css">',
                        "<style>%s</style>" % css)
    page = page.replace('<script src="vendor/leaflet.js"></script>',
                        "<script>%s</script>" % js)
    # 相対パスの写真を data URI に差し替える（DATA の JSON ごと入れ替える）
    old = "const COLOR=%s, DATA=" % json.dumps(BM.FAMILY_COLOR, ensure_ascii=False)
    i = page.index(old)
    j = page.index(";\nconst map=", i)
    page = page[:i] + old + json.dumps(data, ensure_ascii=False) + page[j:]
    page = page.replace('<a href="index.html">ほかの都市</a>', "")
    slug = BM.CITY_SLUG.get(city, city)
    dst = os.path.join(outdir, "%s_地図.html" % city)
    open(dst, "w", encoding="utf-8").write(page)
    mb = os.path.getsize(dst) / 1048576
    print("%-8s %d店 / %.1fMB → %s" % (city, len(sub), mb, dst))
    return dst


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    stores = json.load(open(os.path.join(ROOT, "notion", "stores.json"), encoding="utf-8"))
    for city in BM.CITIES:
        build(city, stores, outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
