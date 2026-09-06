# -*- coding: utf-8 -*-
"""成果物DB の各ガイド行に「場所」（Place）を入れる。

各ガイドは1都市ぶんなので、その都市の全店の座標の中央値をガイドの代表点にする。
中央値を使うのは、外れ値（隣接市の1店など）に引きずられないため。

これで成果物DB に地図ビューが作れる＝57都市の索引地図になり、
ピンをタップするとそのガイドのページが開く。

必要な環境変数:
  NOTION_TOKEN   Notion インテグレーションのトークン
  DRY_RUN        1 なら書き込まない
"""
import json
import os
import statistics
import sys

try:
    import requests
except ImportError:
    sys.exit("requests が要ります: pip install requests")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
UPLOAD_STATE = os.path.join(ROOT, "notion", "state", "upload_state.json")

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"
API = "https://api.notion.com/v1"
VER = os.environ.get("NOTION_VERSION", "2022-06-28")

S = requests.Session()
S.headers.update({"Authorization": "Bearer " + TOKEN, "Notion-Version": VER,
                  "Content-Type": "application/json"})


def main():
    if not TOKEN and not DRY_RUN:
        sys.exit("NOTION_TOKEN がありません")

    stores = json.load(open(STORES, encoding="utf-8"))
    pages = json.load(open(UPLOAD_STATE, encoding="utf-8")).get("pages", {})

    pts, meta = {}, {}
    for s in stores:
        if "lat" not in s or "lng" not in s:
            continue
        g = s["guide"]
        pts.setdefault(g, []).append((s["lat"], s["lng"]))
        meta[g] = (s.get("都市", ""), s.get("国・都道府県", ""))

    ok = miss = fail = 0
    for g in sorted(pts):
        page_id = pages.get(g)
        if not page_id:
            print("ページIDが無い: %s" % g)
            miss += 1
            continue
        lat = statistics.median(p[0] for p in pts[g])
        lon = statistics.median(p[1] for p in pts[g])
        city, area = meta[g]
        name = "%s（%s）" % (city, area) if area else city
        body = {"properties": {"場所": {"place": {
            "name": name, "address": name, "lat": lat, "lon": lon}}}}
        if DRY_RUN:
            print("[dry] %-32s %s %.6f,%.6f (%d店)" % (g, name, lat, lon, len(pts[g])))
            ok += 1
            continue
        r = S.patch("%s/pages/%s" % (API, page_id), data=json.dumps(body))
        if r.status_code >= 300:
            print("失敗 %s: %s %s" % (g, r.status_code, r.text[:200]))
            fail += 1
        else:
            print("OK %-32s %s %.6f,%.6f (%d店)" % (g, name, lat, lon, len(pts[g])))
            ok += 1

    print("---- 成功%d / ページID無し%d / 失敗%d ----" % (ok, miss, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
