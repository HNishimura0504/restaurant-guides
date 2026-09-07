# -*- coding: utf-8 -*-
"""ガイドHTMLから店舗を1店1レコードに抜き出して notion/stores.json を作る。

店舗DB（Notion）へ投入するための中間ファイル。投入経路（公開API／コネクタ）が
どちらに決まっても、この抽出結果はそのまま使える。

使い方:  python notion/stores_extract.py
"""
import io
import os
import re
import sys
import json
import html as htmllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_md import parse_cards, strip_tags   # noqa: E402  カード解析は本文化と同じものを使う

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "notion", "stores.json")
SKIP_DIRS = {".git", ".github", "notion", "map"}

# 店舗DBの「カテゴリ」は11種類。ガイドの見出しは181種類あるので、語で畳む。
# 上から順に当てて、最初に当たったものを採る（順序に意味がある）。
CATEGORY_RULES = [
    ("屋台・食べ歩き", r"屋台|食べ歩き|テイクアウト"),
    ("市場・食材店", r"市場|食材|チーズ|加工肉|惣菜|専門店街|青果|精肉|鮮魚"),
    ("カフェ・パン・スイーツ", r"カフェ|喫茶|パン|ベーカリー|スイーツ|菓子|甘味|ジェラート|アイス"),
    ("ビール・バー", r"ビール|バー|ワイン|地酒|酒どころ|醸造|ブルワリー|パブ"),
    ("居酒屋・焼肉", r"居酒屋|焼肉|焼鳥|炉端|酒場|ホルモン"),
    ("麺類", r"ラーメン|そば|蕎麦|うどん|町中華|麺|パスタ専門"),
    ("寿司・海鮮", r"寿司|鮨|海鮮|うなぎ|鰻|魚"),
    ("アジア・エスニック", r"アジア|中華|韓国|エスニック|タイ|ネパール|インド|ベトナム|中東|アフリカ"),
    ("洋食・各国料理", r"洋食|イタリア|フレンチ|フランス|カレー|各国|欧州|ベルギー料理|中南米|スペイン|ドイツ料理"),
    ("ご当地名物", r"ご当地|名物|郷土"),
    ("和食・郷土料理", r"和食|定食|とんかつ|天ぷら|割烹|料亭|京料理|懐石|会席|郷土料理|日本料理"),
]
# 店の節ではない見出し（モデルコース等）。ここに当たった節は丸ごと捨てる。
NOT_A_STORE_SECTION = r"モデルルート|モデルコース|歩き方|使い方|凡例"


def category_of(heading):
    """見出しをカテゴリへ畳む。

    見出しは「京料理・和食・寿司・鶏料理」のように複数ジャンルが並ぶので、
    **先頭の区切りまでを先に見る**（その節の主題は先頭にある）。
    先頭で決まらなければ見出し全体で当てる。
    """
    head = re.split(r"[・/／(（]", heading)[0]
    for target in (head, heading):
        for name, pat in CATEGORY_RULES:
            if re.search(pat, target):
                return name
    return "和食・郷土料理"   # どれにも当たらない見出しの受け皿


def first_url(s):
    m = re.search(r"\((https?://[^)]+)\)", s)
    return m.group(1) if m else ""


def guide_meta(path, s):
    """HTML自身から 都市（日本語）・国/都道府県・地方 を取る。"""
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    title = htmllib.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else ""
    city = re.sub(r"美食ガイド.*$", "", title).strip()

    head = ""
    cov = re.search(r'<div class="cover">(.*?)\n</div>', s, re.S)
    if cov:
        m = re.search(r'<div style="font-size:8\.5pt[^"]*">(.*?)</div>', cov.group(1), re.S)
        if m:
            head = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()

    region = {"japan": "日本", "europe": "ヨーロッパ", "asia": "アジア"}.get(
        path.replace("\\", "/").split("/")[0], "")
    # 日本は「JAPAN / GIFU・岐阜県 🇯🇵」、国外は「BELGIUM / BRUSSELS 🇧🇪」
    pref = ""
    if "・" in head:
        pref = re.sub(r"\s*[\U0001F1E6-\U0001F1FF]{2}\s*$", "", head.split("・", 1)[1]).strip()
    elif region == "日本":
        # 京都・大阪は表紙が「JAPAN / KYOTO 🇯🇵」で府名が省かれている（都市名と同じため）
        pref = {"京都": "京都府", "大阪": "大阪府"}.get(city, "")
    else:
        country = {"belgium": "ベルギー", "france": "フランス", "germany": "ドイツ",
                   "netherlands": "オランダ", "nepal": "ネパール"}
        pref = country.get(path.replace("\\", "/").split("/")[1], "")
    return title, city, pref, region


def card_ids(block):
    return re.findall(r'<div class="card" id="c-([^"]+)"', block)


def main():
    out, skipped = [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".html"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            s = io.open(full, encoding="utf-8").read()
            base = rel[:-5].replace("/", "_")
            title, city, pref, region = guide_meta(rel, s)

            slug = fn[:-5]
            loc_path = os.path.join(dirpath, "control", "locations_%s.json" % slug)
            locs = json.load(io.open(loc_path, encoding="utf-8")) if os.path.isfile(loc_path) else {}

            body = s.split("<body>", 1)[1].rsplit("</body>", 1)[0]
            parts = re.split(r"<h2\b[^>]*>(.*?)</h2>", body, flags=re.S)
            for i in range(1, len(parts), 2):
                heading = strip_tags(parts[i], False)
                if re.search(NOT_A_STORE_SECTION, heading):
                    skipped.append((base, heading))
                    continue
                block = parts[i + 1]
                ids = card_ids(block)
                cards = parse_cards(block)
                if len(ids) != len(cards):
                    print("   ! %s / %s: id=%d cards=%d（対応が取れないので id を付けない）"
                          % (base, heading, len(ids), len(cards)))
                    ids = [""] * len(cards)
                for cid, c in zip(ids, cards):
                    rec = {
                        "guide": base, "guide_title": title,
                        "都市": city, "国・都道府県": pref, "地方": region,
                        "slug": cid,
                        "店名": c["name"], "よみ": c["yomi"],
                        "地図番号": int(c["no"]) if c["no"].isdigit() else None,
                        "章（原文）": heading, "カテゴリ": category_of(heading),
                        "タグ": c["chips"], "説明": c["desc"], "一皿": c["sig"],
                        "選定理由": c["reason"],
                        "Googleマップ": c["map"], "参照元": first_url(c["src"]),
                    }
                    for k, v in c["info"]:
                        if k in ("営業時間", "定休日", "住所", "予約"):
                            rec[k] = v
                    if cid and cid in locs:
                        rec["lat"] = locs[cid]["lat"]
                        rec["lng"] = locs[cid]["lng"]
                    out.append(rec)

    fh = io.open(OUT, "w", encoding="utf-8", newline="\n")
    fh.write(json.dumps(out, ensure_ascii=False, indent=1))
    fh.close()

    print("---")
    print("店舗           : %d" % len(out))
    print("ガイド         : %d" % len(set(r["guide"] for r in out)))
    print("緯度経度あり   : %d" % sum(1 for r in out if "lat" in r))
    print("住所あり       : %d" % sum(1 for r in out if r.get("住所")))
    print("捨てた節       : %d  %s" % (len(skipped), skipped[:3]))
    import collections
    print("カテゴリ内訳   :")
    for k, v in collections.Counter(r["カテゴリ"] for r in out).most_common():
        print("   %-22s %4d" % (k, v))
    empty = [r["guide"] for r in out if not r["都市"] or not r["国・都道府県"]]
    print("都市/県が空    : %d %s" % (len(empty), sorted(set(empty))[:5]))


if __name__ == "__main__":
    main()
