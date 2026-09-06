# -*- coding: utf-8 -*-
"""対象都市の店を Places API (New) の Text Search で引き、place_id と写真リソース名を保存する。

なぜ Places か（2026-09-06 の方針変更）:
  Street View は座標から見えるものを撮るので、テナントの入れ替わりと座標の誤差を吸収できない。
  実測で「店構えが分かる」のは約1/3だった。**Places の写真は place_id に紐づくので、
  別の店が写ることが原理的に起きない。** 経緯 = topics/restaurant-guides/notes/map_photos_requirements.md §5-3

費用: フィールドマスクに photos を含めるので Text Search Pro（月5,000件無料）。5都市298店なら無料枠内。

必要な環境変数:
  MAPS_KEY   Google Maps Platform の APIキー（**コミットしない**）
  CITIES     対象都市をカンマ区切りで（既定 = 大阪,京都,吹田,東京23区,ルーベン）
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
OUT = os.path.join(ROOT, "notion", "state", "places_5cities.json")

KEY = os.environ.get("MAPS_KEY", "").strip()
CITIES = [c for c in os.environ.get(
    "CITIES", "大阪,京都,吹田,東京23区,ルーベン").split(",") if c]
LIMIT = int(os.environ.get("LIMIT", "0") or 0)

URL = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ("places.id,places.displayName,places.formattedAddress,places.location,"
          "places.businessStatus,places.photos")

S = requests.Session()


def search(query, bias=None):
    body = {"textQuery": query, "maxResultCount": 3}
    if bias:
        body["locationBias"] = {"circle": {
            "center": {"latitude": bias[0], "longitude": bias[1]},
            "radius": 500.0}}
    r = S.post(URL, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": KEY,
        "X-Goog-FieldMask": FIELDS,
        "Referer": "https://claude.ai/",
    }, data=json.dumps(body), timeout=40)
    if r.status_code != 200:
        return {"_error": "%s %s" % (r.status_code, r.text[:200])}
    return r.json()


def main():
    if not KEY:
        sys.exit("MAPS_KEY がありません")
    stores = [s for s in json.load(open(STORES, encoding="utf-8"))
              if s.get("都市") in CITIES]
    stores.sort(key=lambda s: (s["guide"], s["slug"]))
    if LIMIT:
        stores = stores[:LIMIT]

    out = {}
    if os.path.exists(OUT):
        out = json.load(open(OUT, encoding="utf-8"))

    ok = skip = miss = err = 0
    for i, s in enumerate(stores, 1):
        key = "%s/%s" % (s["guide"], s["slug"])
        if key in out and out[key].get("place_id"):
            skip += 1
            continue
        q = "%s %s" % (s["店名"], s.get("住所") or s.get("都市", ""))
        bias = (s["lat"], s["lng"]) if "lat" in s and "lng" in s else None
        res = search(q, bias)
        if "_error" in res:
            print("[%d] %s API エラー: %s" % (i, s["店名"], res["_error"]))
            err += 1
            continue
        places = res.get("places") or []
        if not places:
            print("[%d] %s → Places に見つからない" % (i, s["店名"]))
            out[key] = {"status": "NOT_FOUND"}
            miss += 1
            continue
        p = places[0]
        out[key] = {
            "place_id": p.get("id"),
            "display": (p.get("displayName") or {}).get("text"),
            "address": p.get("formattedAddress"),
            "businessStatus": p.get("businessStatus"),
            "photo_names": [ph.get("name") for ph in (p.get("photos") or [])],
            "店名": s["店名"],
            "都市": s["都市"],
        }
        ok += 1
        if i % 25 == 0:
            print("  ... %d/%d" % (i, len(stores)))
            os.makedirs(os.path.dirname(OUT), exist_ok=True)
            json.dump(out, open(OUT, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
        time.sleep(0.05)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("---- 取得%d / 既取得%d / 見つからない%d / エラー%d ----"
          % (ok, skip, miss, err))
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
