# -*- coding: utf-8 -*-
"""notion/stores.json の店を、Notion の店舗DBへ投入する（作成または更新）。

場所（Place）プロパティは公開APIで書ける。形は {"place": {"lat": 数値, "lon": 数値, ...}}
（`notion/place_probe.py` で実測。lat と lon は両方必須で、経度の名前は lon）。

同じ店を二重に作らないための鍵は「キー」プロパティ（`<ガイド>/<slug>`）。
既存の12行（ルーベン）はキーが空なので、初回だけ (都市, 店名) で突き合わせてキーを埋める。

必要な環境変数:
  NOTION_TOKEN   Notion インテグレーションのトークン
  STORES_DB_ID   店舗DBのID（既定あり）
  LIMIT          1回で処理する件数の上限（0＝全部）
  DRY_RUN        1 なら書き込まない
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
    sys.exit("requests が要ります: pip install requests")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
MAP_TSV = os.path.join(ROOT, "notion", "map.tsv")
STATE = os.path.join(ROOT, "notion", "state", "stores_state.json")

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DB_ID = (os.environ.get("STORES_DB_ID") or "7ef49bd2-f83d-4b45-9df2-726ebec1fe77").strip()
LIMIT = int(os.environ.get("LIMIT", "0") or 0)
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"
API = "https://api.notion.com/v1"
VER = os.environ.get("NOTION_VERSION", "2022-06-28")

# multi_select は知らない名前を渡すと選択肢が勝手に増えるので、既存の9個だけに絞る。
KNOWN_TAGS = {"地元密着", "口コミ突出", "老舗・歴史", "ブログ推薦", "ベジ対応",
              "食の専門街・市場", "眺望", "隣接市", "権威評価"}

S = requests.Session()
S.headers.update({"Authorization": "Bearer " + TOKEN, "Notion-Version": VER,
                  "Content-Type": "application/json"})


def api(method, path, **kw):
    for attempt in range(6):
        r = S.request(method, API + path, timeout=120, **kw)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2)))
            continue
        if r.status_code >= 500:
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code >= 400:
            raise RuntimeError("%s %s -> %s %s" % (method, path, r.status_code, r.text[:300]))
        return r.json() if r.text else {}
    raise RuntimeError("retries exhausted: %s %s" % (method, path))


def txt(v):
    return {"rich_text": [{"type": "text", "text": {"content": (v or "")[:2000]}}]}


def url_or_none(v):
    v = (v or "").strip()
    return {"url": v if re.match(r"^https?://", v) else None}


def load_guide_pages():
    """notion/map.tsv: <ガイド> <ページID> <タイトル>"""
    m = {}
    if os.path.isfile(MAP_TSV):
        for ln in io.open(MAP_TSV, encoding="utf-8"):
            f = ln.rstrip("\n").split("\t")
            if len(f) >= 2 and f[1] and f[1] != "NEW":
                m[f[0]] = f[1]
    return m


def props_of(rec, guide_page):
    p = {
        "店名": {"title": [{"type": "text", "text": {"content": rec["店名"][:2000]}}]},
        "キー": txt("%s/%s" % (rec["guide"], rec["slug"])),
        "よみ": txt(rec.get("よみ")),
        "一皿": txt(rec.get("一皿")),
        "説明": txt(rec.get("説明")),
        "選定理由": txt(rec.get("選定理由")),
        "章（原文）": txt(rec.get("章（原文）")),
        "住所": txt(rec.get("住所")),
        "営業時間": txt(rec.get("営業時間")),
        "定休日": txt(rec.get("定休日")),
        "予約": txt(rec.get("予約")),
        "Googleマップ": url_or_none(rec.get("Googleマップ")),
        "参照元": url_or_none(rec.get("参照元")),
    }
    for name in ("カテゴリ", "都市", "国・都道府県"):
        if rec.get(name):
            p[name] = {"select": {"name": rec[name]}}
    tags = [t for t in (rec.get("タグ") or []) if t in KNOWN_TAGS]
    p["タグ"] = {"multi_select": [{"name": t} for t in tags]}
    if rec.get("地図番号") is not None:
        p["地図番号"] = {"number": rec["地図番号"]}
    if guide_page:
        p["掲載ガイド"] = {"relation": [{"id": guide_page}]}
    if "lat" in rec and "lng" in rec:
        p["場所"] = {"place": {"lat": rec["lat"], "lon": rec["lng"],
                              "name": rec["店名"][:200],
                              "address": (rec.get("住所") or "")[:300]}}
    return p


def fetch_existing():
    """店舗DBの既存行を全部読み、キーと (都市, 店名) の索引を作る。"""
    by_key, by_name = {}, {}
    cur = None
    while True:
        body = {"page_size": 100}
        if cur:
            body["start_cursor"] = cur
        res = api("POST", "/databases/%s/query" % DB_ID, json=body)
        for pg in res.get("results", []):
            pr = pg.get("properties", {})
            def plain(name):
                v = pr.get(name) or {}
                arr = v.get("rich_text") or v.get("title") or []
                return "".join(x.get("plain_text", "") for x in arr)
            key = plain("キー")
            name = plain("店名")
            city = ((pr.get("都市") or {}).get("select") or {}).get("name", "")
            if key:
                by_key[key] = pg["id"]
            if name:
                by_name[(city, name)] = pg["id"]
        if not res.get("has_more"):
            break
        cur = res.get("next_cursor")
    return by_key, by_name


def main():
    if not TOKEN and not DRY_RUN:
        sys.exit("NOTION_TOKEN が設定されていません")

    recs = json.load(io.open(STORES, encoding="utf-8"))
    guides = load_guide_pages()
    state = json.load(io.open(STATE, encoding="utf-8")) if os.path.isfile(STATE) else {}

    if DRY_RUN:
        by_key, by_name = dict(state), {}
    else:
        print("既存行を読み込み中…")
        by_key, by_name = fetch_existing()
        by_key.update({k: v for k, v in state.items() if k not in by_key})
        print("既存 %d 行（キーあり %d）" % (len(by_name), len(by_key)))

    todo = recs[:LIMIT] if LIMIT else recs
    created = updated = skipped = 0
    no_guide = set()

    for i, rec in enumerate(todo, 1):
        key = "%s/%s" % (rec["guide"], rec["slug"])
        gp = guides.get(rec["guide"])
        if not gp:
            no_guide.add(rec["guide"])
        p = props_of(rec, gp)
        pid = by_key.get(key) or by_name.get((rec.get("都市", ""), rec["店名"]))

        if DRY_RUN:
            skipped += 1
        elif pid:
            api("PATCH", "/pages/" + pid, json={"properties": p})
            by_key[key] = pid
            updated += 1
        else:
            res = api("POST", "/pages",
                      json={"parent": {"database_id": DB_ID}, "properties": p})
            by_key[key] = res["id"]
            created += 1

        if i % 100 == 0:
            print("  %d / %d （作成 %d・更新 %d）" % (i, len(todo), created, updated))
            if not DRY_RUN:
                save_state(by_key)

    if not DRY_RUN:
        save_state(by_key)
    print("---")
    print("作成 %d / 更新 %d / 対象 %d" % (created, updated, len(todo)))
    if DRY_RUN:
        print("[dry] 書き込みはしていない（%d 件を組み立てただけ）" % skipped)
    if no_guide:
        print("! 掲載ガイドのページIDが引けなかったガイド: %s" % sorted(no_guide))


def save_state(by_key):
    d = os.path.dirname(STATE)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    fh = io.open(STATE, "w", encoding="utf-8", newline="\n")
    fh.write(json.dumps(by_key, ensure_ascii=False, indent=1))
    fh.close()


if __name__ == "__main__":
    main()
