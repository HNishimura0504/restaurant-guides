# -*- coding: utf-8 -*-
"""取得した座標が、その都市の店として妥当な位置にあるかを検査する。

Places の Text Search は「店名＋住所」で引いた先頭の1件を採るので、
同名店・閉業・表記ゆれで**別の土地の店を掴むことがある**。
1件ずつ目視はできないので、**都市ごとの中央値からの距離**で外れ値を出す。

判定: 都市の中央値から 50km 超を「疑わしい」として列挙する。
（1つの市の中に収まるガイドなので、正しく引けていれば数km以内に収まる。
 「隣接市」タグの店があるため、閾値は緩めに取る。）

使い方:  python notion/locations_check.py
"""
import io
import os
import json
import math
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
FAR_KM = 50.0


def km(a, b):
    """2点間の距離（km）。ざっくりで十分なので球面近似。"""
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(min(1.0, math.sqrt(d)))


def guide_dir(guide):
    region, rest = guide.split("_", 1)
    country, city = rest.rsplit("_", 1)
    return os.path.join(ROOT, region, country), city


def main():
    stores = json.load(io.open(STORES, encoding="utf-8"))
    by_guide = {}
    for r in stores:
        by_guide.setdefault(r["guide"], []).append(r)

    total = with_loc = suspect = 0
    rows = []
    for guide in sorted(by_guide):
        d, city = guide_dir(guide)
        path = os.path.join(d, "control", "locations_%s.json" % city)
        locs = json.load(io.open(path, encoding="utf-8")) if os.path.isfile(path) else {}
        pts = []
        for r in by_guide[guide]:
            total += 1
            p = locs.get(r["slug"])
            if p:
                with_loc += 1
                pts.append((p["lat"], p["lng"], r["店名"]))
        if len(pts) < 3:
            continue
        mid = (statistics.median(p[0] for p in pts), statistics.median(p[1] for p in pts))
        far = [(km(mid, (p[0], p[1])), p[2], p[0], p[1]) for p in pts]
        far = [f for f in far if f[0] > FAR_KM]
        suspect += len(far)
        if far:
            rows.append((guide, mid, sorted(far, reverse=True)))

    print("店舗 %d / 座標あり %d / 疑わしい %d" % (total, with_loc, suspect))
    for guide, mid, far in rows:
        print("\n== %s  中央値 %.4f,%.4f" % (guide, mid[0], mid[1]))
        for dist, name, la, lo in far[:10]:
            print("   %7.1fkm  %-28s %.4f,%.4f" % (dist, name[:28], la, lo))


if __name__ == "__main__":
    main()
