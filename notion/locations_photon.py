# -*- coding: utf-8 -*-
"""海外の店に、Photon（Komoot・OSM ベース）で緯度経度を付ける。キーも課金も要らない。

**なぜ Photon か**: 2026-09-16 のユーザー指示「Google cloud は有料版入らない」により
Places API を使わない。無料の候補を実測した結果（`maps_platform_free_migration.md`）、

| API | 成功 | 誤差 | キー | 範囲 |
|---|---|---|---|---|
| **Photon** `photon.komoot.io/api` | **8/8** | **中央値 7m・最大 18m** | 不要 | **世界** |
| Nominatim | 2/8（6件が **HTTP 429**） | 3〜22m | 不要 | 世界 |
| 国土地理院 住所検索API | 全件 | 中央値 15m | 不要 | **日本国内のみ** |

**＝海外の都市では国土地理院が使えない**ので、Photon を主に使う。

**採否の判定（規約 §21-6・`notion_map_embed_2026.md` の「判定の原則」）**:
`limit=1` の地名検索は**必ず何かを返す**ので、ヒット率は品質の指標にならない。採否は

  ①その都市の基準点からの距離（既定 30km 以内。町が散る湾岸・島は引数で広げる）
  ②**返ってきた名前が、探している店名か住所の要素と一致するか**

の**2つ両方**で決める。**②を省くと、同名の別の町の店を掴む。**
どちらかを満たさない候補は捨て、次の候補を見る。全部落ちたら **その店は未解決として残す**
（憶測の座標を入れない。未解決は呼び出し側が目視で埋める）。

**礼儀**: 1件ごとに1.1秒空ける（公開エンドポイントへの連打をしない）。

使い方:
  python3 notion/locations_photon.py <research.json> <out.json> <基準緯度> <基準経度> [半径km]
例:
  python3 notion/locations_photon.py /tmp/research_hilo_raw.json \\
      japan/../north_america/usa/control/locations_hilo.json 19.7297 -155.0900 40
"""
import io
import json
import math
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

UA = "restaurant-guides/1.0 (personal food guide; contact via GitHub HNishimura0504)"
API = "https://photon.komoot.io/api"


def norm(s):
    """比較用に字面をならす。アクセント記号を落とし、記号と空白を抜く。"""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def hav(a, b, c, d):
    """2点間の距離（km）。"""
    r = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp = math.radians(c - a)
    dl = math.radians(d - b)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))


def ask(q, lat, lng, limit=5):
    url = "%s?%s" % (API, urllib.parse.urlencode(
        {"q": q, "limit": limit, "lat": "%.4f" % lat, "lon": "%.4f" % lng}))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8")).get("features", [])


def accept(feat, name, addr, lat0, lng0, radius):
    """①距離 ②名前か住所の一致、の2つ両方を満たすか。満たせば (lat, lng, 理由)。"""
    c = feat.get("geometry", {}).get("coordinates")
    if not c or len(c) != 2:
        return None
    lng, lat = c[0], c[1]
    d = hav(lat0, lng0, lat, lng)
    if d > radius:
        return None                                   # ①で落ちる
    p = feat.get("properties", {})
    pname = norm(p.get("name", ""))
    nm = norm(name)
    hit = ""
    if pname and (pname in nm or nm in pname):
        hit = "店名一致"
    else:
        # 住所の一致で代替する。番地と通り名の両方が要る（通り名だけだと通りの中点を掴む）。
        num = re.match(r"\s*(\d+[-\w]*)", addr or "")
        street = norm(re.sub(r"^\s*\d+[-\w]*\s*,?\s*", "", addr or "").split(",")[0])
        pstreet = norm(p.get("street", ""))
        pnum = norm(p.get("housenumber", ""))
        if street and pstreet and (street in pstreet or pstreet in street):
            if num and pnum and norm(num.group(1)) == pnum:
                hit = "番地一致"
            elif not num:
                hit = "通り一致"
    if not hit:
        return None                                   # ②で落ちる
    return (lat, lng, "%s / %.1fkm" % (hit, d))


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    lat0, lng0 = float(sys.argv[3]), float(sys.argv[4])
    radius = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0

    data = json.load(io.open(src, encoding="utf-8"))
    stores = data["stores"] if isinstance(data, dict) else data
    got, miss = {}, []
    for s in stores:
        sid, name, addr = s["id"], s["name"], s.get("address", "")
        res = None
        for q in ("%s, %s" % (name, addr), addr, name):
            if not q.strip(" ,"):
                continue
            try:
                feats = ask(q, lat0, lng0)
            except Exception as e:
                print("   ! 問い合わせ失敗 %s: %s" % (sid, e))
                feats = []
            time.sleep(1.1)
            for f in feats:
                res = accept(f, name, addr, lat0, lng0, radius)
                if res:
                    break
            if res:
                break
        if res:
            got[sid] = {"lat": round(res[0], 7), "lng": round(res[1], 7)}
            print("%-28s %.5f, %.5f  (%s)" % (sid, res[0], res[1], res[2]))
        else:
            miss.append(sid)
            print("%-28s 未解決" % sid)

    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(got, ensure_ascii=False, indent=1))
    print("\n解決 %d / %d 件。未解決 %d 件: %s"
          % (len(got), len(stores), len(miss), ", ".join(miss) or "なし"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
