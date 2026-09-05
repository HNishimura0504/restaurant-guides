# -*- coding: utf-8 -*-
"""座標を持たない店に、Places API (New) の Text Search で緯度経度を付ける。

Notion の場所プロパティは lat/lon が必須（住所の文字列だけでは地図に載らない）と実測で分かったため。
Geocoding API はこのキーで有効になっていないが、**Places API (New) は有効**で、
テキスト検索の応答に location（緯度経度）が入るので、そちらを使う。

結果は各ガイドの control/locations_<市>.json（既存と同じ {slug: {lat, lng}} の形）へ書き足す。
ガイドの地図画像を作る仕組みも同じファイルを読むので、そちらでも使える。

環境変数: MAPS_KEY（コマンド内でのみ使う。リポジトリにも成果物にも残さない）
        LIMIT（試すときの上限。0＝全部）
"""
import io
import os
import re
import sys
import json
import time

try:
    import requests
except ImportError:
    sys.exit("requests が要ります")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
KEY = os.environ.get("MAPS_KEY", "").strip()
LIMIT = int(os.environ.get("LIMIT", "0") or 0)
URL = "https://places.googleapis.com/v1/places:searchText"

if not KEY:
    sys.exit("MAPS_KEY が要ります")

S = requests.Session()
S.headers.update({
    "Content-Type": "application/json",
    "X-Goog-Api-Key": KEY,
    # キーは HTTP リファラー制限つきなので、この見出しが要る（AI_memory.md §4）
    "Referer": "https://claude.ai/",
    "X-Goog-FieldMask": "places.id,places.location,places.formattedAddress,places.displayName",
})


def guide_dir(guide):
    """japan_gifu_gifu -> (japan/gifu, gifu)"""
    region, rest = guide.split("_", 1)
    country, city = rest.rsplit("_", 1)
    return os.path.join(ROOT, region, country), city


def search(query):
    for attempt in range(4):
        r = S.post(URL, json={"textQuery": query, "languageCode": "ja"}, timeout=60)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code >= 400:
            return None, "%s %s" % (r.status_code, r.text[:200])
        places = r.json().get("places") or []
        if not places:
            return None, "該当なし"
        p = places[0]
        return p, ""
    return None, "リトライ尽きた"


def main():
    stores = json.load(io.open(STORES, encoding="utf-8"))
    todo = [r for r in stores if "lat" not in r and r["slug"] and r.get("住所")]
    if LIMIT:
        todo = todo[:LIMIT]
    print("対象 %d 件" % len(todo))

    by_guide = {}
    for r in todo:
        by_guide.setdefault(r["guide"], []).append(r)

    ok = ng = 0
    failures = []
    for guide in sorted(by_guide):
        d, city = guide_dir(guide)
        path = os.path.join(d, "control", "locations_%s.json" % city)
        locs = json.load(io.open(path, encoding="utf-8")) if os.path.isfile(path) else {}
        got = 0
        for r in by_guide[guide]:
            if r["slug"] in locs:
                continue
            q = "%s %s" % (r["店名"], r["住所"])
            p, err = search(q)
            if not p:
                ng += 1
                failures.append((guide, r["店名"], err))
                continue
            loc = p["location"]
            locs[r["slug"]] = {"lat": loc["latitude"], "lng": loc["longitude"]}
            ok += 1
            got += 1
        if got:
            if not os.path.isdir(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            fh = io.open(path, "w", encoding="utf-8", newline="\n")
            fh.write(json.dumps(locs, ensure_ascii=False, indent=1))
            fh.close()
        print("%-34s +%d (計 %d)" % (guide, got, len(locs)))

    print("---")
    print("取得 %d / 失敗 %d" % (ok, ng))
    for f in failures[:20]:
        print("  ! %s / %s -> %s" % f)


if __name__ == "__main__":
    main()
