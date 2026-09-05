# -*- coding: utf-8 -*-
"""公開 Notion API で place（場所）プロパティに書き込めるかを実測する。

Notion の API リファレンス（property object）には
「Place page property values are not fully supported via the API」とある。
店舗DB 約2,900行の投入を GitHub Actions のスクリプトでやれるか、
それともこのリポジトリの外（Notion コネクタ経由）でしかできないかが、これで決まる。

環境変数: NOTION_TOKEN, PROBE_PAGE_ID（書き込み先の1行）
"""
import os
import sys
import json
import requests

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
PAGE = os.environ.get("PROBE_PAGE_ID", "").strip()
PROP = os.environ.get("PROBE_PROP", "場所")
VER = os.environ.get("NOTION_VERSION", "2022-06-28")
API = "https://api.notion.com/v1"

if not TOKEN or not PAGE:
    sys.exit("NOTION_TOKEN と PROBE_PAGE_ID が要ります")

S = requests.Session()
S.headers.update({"Authorization": "Bearer " + TOKEN, "Notion-Version": VER})


def show(label, r):
    print("--- %s -> %s" % (label, r.status_code))
    print(r.text[:900])
    print()


print("== 1. まず現在の値を読む ==")
r = S.get("%s/pages/%s" % (API, PAGE), timeout=60)
if r.status_code < 400:
    props = r.json().get("properties", {})
    print("%s = %s" % (PROP, json.dumps(props.get(PROP), ensure_ascii=False)))
else:
    show("GET page", r)

print("== 2. 書き込みを試す（3通りの形） ==")
shapes = {
    "lat/lng": {"place": {"lat": 50.8784, "lng": 4.7006,
                          "name": "Wurst", "address": "Margarethaplein 1, 3000 Leuven"}},
    "lat/long": {"place": {"lat": 50.8784, "long": 4.7006, "name": "Wurst"}},
    "lat/lon": {"place": {"lat": 50.8784, "lon": 4.7006, "name": "Wurst"}},
    "lat/longitude": {"place": {"lat": 50.8784, "longitude": 4.7006, "name": "Wurst"}},
    "lat のみ": {"place": {"lat": 50.8784}},
}
for label, value in shapes.items():
    r = S.patch("%s/pages/%s" % (API, PAGE), json={"properties": {PROP: value}}, timeout=60)
    show(label, r)
    if r.status_code < 400:
        r2 = S.get("%s/pages/%s" % (API, PAGE), timeout=60)
        got = r2.json().get("properties", {}).get(PROP)
        print("   読み戻し: %s" % json.dumps(got, ensure_ascii=False))
        print("   => 書き込みが残ったか: %s" % ("はい" if got and got.get("place") else "いいえ（null のまま）"))
        print()
