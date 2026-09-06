# -*- coding: utf-8 -*-
"""店の外観写真を Street View Static API で取得する。

なぜ Street View か:
  外観（店構え）の実写が要る。Places の写真（Place Photos）は Enterprise 階層で
  月1,000件しか無料枠が無く、3,054店だと課金対象になる。
  Street View Static は Essentials 階層で月10,000件無料。用途としても店構えの実写で合う。
  出典 = topics/restaurant-guides/notes/map_photos_requirements.md §2-2

手順（HNishimura0504/test の CLAUDE.md「実写取得の確立済み手順」に従う）:
  1. metadata で status と pano の座標を確認する
  2. pano から店へ向かう方位角を計算し、heading に渡す（そうしないと道の反対側を向く）
  3. 画像を取得する
  4. **取得した写真は必ず1枚ずつ目視確認する**（広場・工事中などで店が写らない地点がある）

リファラー制限（HTTPリファラー claude.ai）があるので Referer ヘッダーが必須。

必要な環境変数:
  MAPS_KEY   Google Maps Platform の APIキー（**コミットしない**）
  CITIES     対象都市をカンマ区切りで（既定 = 大阪,京都,吹田,東京23区,ルーベン）
  LIMIT      処理件数の上限（0=全部）
  DRY_RUN    1 なら metadata だけ引いて画像は取らない
"""
import json
import math
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("requests が要ります: pip install requests")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
STATE = os.path.join(ROOT, "notion", "state", "streetview_state.json")

KEY = os.environ.get("MAPS_KEY", "").strip()
CITIES = [c for c in os.environ.get(
    "CITIES", "大阪,京都,吹田,東京23区,ルーベン").split(",") if c]
LIMIT = int(os.environ.get("LIMIT", "0") or 0)
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"

BASE = "https://maps.googleapis.com/maps/api/streetview"
S = requests.Session()
S.headers.update({"Referer": "https://claude.ai/"})


def bearing(lat1, lon1, lat2, lon2):
    """1点目から2点目へ向かう方位角（度・北が0）。"""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


# Street View には店や施設が自分で上げた「屋内のパノラマ」が混ざっている。
# `source=outdoor` を渡してもこれは除外されない（2026-09-06 実測。ルーベンの ahquy で
# `© Pentahotel Leuven` の屋内パノラマが返り、店内の写真になった）。
# 見分けは `copyright` フィールドで、道路から撮った公式のものだけが `© Google`。
# 店の真上に道路パノラマが無いことはあるので、見つからなければ周囲4方向へ約30mずらして探す。
GOOGLE_COPYRIGHT = "© Google"
OFFSETS_M = 30.0


def _meta(lat, lng, radius):
    r = S.get(BASE + "/metadata",
              params={"location": "%s,%s" % (lat, lng), "source": "outdoor",
                      "radius": radius, "key": KEY}, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"status": "PARSE_ERROR"}


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_google_pano(lat, lng):
    """道路から撮った公式パノラマ（© Google）の metadata を返す。無ければ None。

    **近い順に探す。** 半径を 25→40→60m と広げ、最初に見つかった © Google を採る。
    遠いパノラマほど店が小さく写り、隣の建物が入りやすいので、近さが画の質を決める。
    それでも無ければ周囲4方向へ約30mずらして探す（店の真上に道路が無い場合）。
    """
    for radius in (25, 40, 60):
        m = _meta(lat, lng, radius)
        if m.get("status") == "OK" and m.get("copyright") == GOOGLE_COPYRIGHT:
            return m
    dlat = OFFSETS_M / 111320.0
    dlng = OFFSETS_M / (111320.0 * max(math.cos(math.radians(lat)), 1e-6))
    for dy, dx in ((dlat, 0), (-dlat, 0), (0, dlng), (0, -dlng)):
        m = _meta(lat + dy, lng + dx, 40)
        if m.get("status") == "OK" and m.get("copyright") == GOOGLE_COPYRIGHT:
            return m
    return None


def out_path(store):
    parts = store["guide"].split("_")
    return os.path.join(ROOT, parts[0], parts[1], "img", parts[2],
                        store["slug"] + "_exterior.jpg")


def main():
    if not KEY:
        sys.exit("MAPS_KEY がありません")
    stores = [s for s in json.load(open(STORES, encoding="utf-8"))
              if s.get("都市") in CITIES and "lat" in s and "lng" in s]
    stores.sort(key=lambda s: (s["guide"], s["slug"]))
    if LIMIT:
        stores = stores[:LIMIT]
    print("対象 %d 店（都市: %s）" % (len(stores), ",".join(CITIES)))

    state = {}
    if os.path.exists(STATE):
        state = json.load(open(STATE, encoding="utf-8"))

    ok = skip = nopano = fail = 0
    for i, s in enumerate(stores, 1):
        key = "%s/%s" % (s["guide"], s["slug"])
        dst = out_path(s)
        if os.path.exists(dst) and state.get(key, {}).get("status") == "OK":
            skip += 1
            continue

        meta = find_google_pano(s["lat"], s["lng"])
        if meta is None:
            print("[%d] %s → 道路のパノラマが見つからない（撮影地点なし）" % (i, s["店名"]))
            state[key] = {"status": "NO_GOOGLE_PANO"}
            nopano += 1
            continue

        pano = meta.get("pano_id")
        ploc = meta.get("location", {})
        head = bearing(ploc.get("lat", s["lat"]), ploc.get("lng", s["lng"]),
                       s["lat"], s["lng"])
        dist = haversine_m(ploc.get("lat", s["lat"]), ploc.get("lng", s["lng"]),
                           s["lat"], s["lng"])
        # 近いほど画角を狭くする。遠いところから狭い画角で撮ると隣の建物しか写らない。
        fov = 70 if dist < 12 else (90 if dist < 25 else 110)
        state[key] = {"status": "OK", "pano": pano, "heading": round(head, 1),
                      "dist_m": round(dist, 1), "fov": fov,
                      "date": meta.get("date"), "copyright": meta.get("copyright")}
        if DRY_RUN:
            ok += 1
            continue

        img = S.get(BASE, params={"size": "640x400", "pano": pano,
                                  "heading": round(head, 1), "fov": fov,
                                  "pitch": 5, "key": KEY}, timeout=60)
        if img.status_code != 200 or not img.content:
            print("[%d] %s 画像取得に失敗 %s" % (i, s["店名"], img.status_code))
            fail += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(img.content)
        ok += 1
        if i % 25 == 0:
            print("  ... %d/%d" % (i, len(stores)))
            os.makedirs(os.path.dirname(STATE), exist_ok=True)
            json.dump(state, open(STATE, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
        time.sleep(0.05)

    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(state, open(STATE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("---- 取得%d / 既取得%d / 撮影地点なし%d / 失敗%d ----"
          % (ok, skip, nopano, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
