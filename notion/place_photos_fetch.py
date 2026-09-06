# -*- coding: utf-8 -*-
"""Places の写真を店ごとに数枚ずつ取り、外観を目視で選べるようにする。

費用: Place Photos は Enterprise 階層で**月1,000件しか無料枠が無い**。
  5都市298店 × 3枚 = 894件で無料枠内に収まる。**1店あたりの枚数を増やすと超える。**
  出典 = https://developers.google.com/maps/documentation/places/web-service/usage-and-billing

出力: <地方>/<県>/img/<都市>/<slug>_c1.jpg 〜 _c3.jpg（c = candidate・候補）
  選んだ1枚を後から `_exterior.jpg` にする。候補は選定後に消す。

必要な環境変数:
  MAPS_KEY   Google Maps Platform の APIキー（**コミットしない**）
  PER_STORE  1店あたりの候補枚数（既定3）
  LIMIT      処理件数の上限（0=全部）
"""
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("requests が要ります: pip install requests")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
PLACES = os.path.join(ROOT, "notion", "state", "places_5cities.json")

KEY = os.environ.get("MAPS_KEY", "").strip()
PER_STORE = int(os.environ.get("PER_STORE", "3"))
LIMIT = int(os.environ.get("LIMIT", "0") or 0)

S = requests.Session()
S.headers.update({"Referer": "https://claude.ai/"})


def out_dir(store):
    p = store["guide"].split("_")
    return os.path.join(ROOT, p[0], p[1], "img", p[2])


def main():
    if not KEY:
        sys.exit("MAPS_KEY がありません")
    places = json.load(open(PLACES, encoding="utf-8"))
    idx = {"%s/%s" % (s["guide"], s["slug"]): s
           for s in json.load(open(STORES, encoding="utf-8"))}

    keys = [k for k in sorted(places) if places[k].get("photo_names")]
    if LIMIT:
        keys = keys[:LIMIT]
    print("対象 %d 店 × 最大 %d 枚 = %d 回" % (len(keys), PER_STORE,
                                              len(keys) * PER_STORE))

    got = skip = fail = 0
    for i, k in enumerate(keys, 1):
        s = idx.get(k)
        if not s:
            continue
        d = out_dir(s)
        os.makedirs(d, exist_ok=True)
        for j, name in enumerate(places[k]["photo_names"][:PER_STORE], 1):
            dst = os.path.join(d, "%s_c%d.jpg" % (s["slug"], j))
            if os.path.exists(dst) and os.path.getsize(dst) > 1000:
                skip += 1
                continue
            r = S.get("https://places.googleapis.com/v1/%s/media" % name,
                      params={"maxWidthPx": 640, "key": KEY}, timeout=60)
            if r.status_code != 200 or len(r.content) < 1000:
                print("[%d] %s c%d 失敗 %s" % (i, s["店名"], j, r.status_code))
                fail += 1
                continue
            with open(dst, "wb") as f:
                f.write(r.content)
            got += 1
            time.sleep(0.05)
        if i % 25 == 0:
            print("  ... %d/%d" % (i, len(keys)))

    print("---- 取得%d / 既取得%d / 失敗%d ----" % (got, skip, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
