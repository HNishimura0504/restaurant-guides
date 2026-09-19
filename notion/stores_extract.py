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
    ("カフェ・パン・スイーツ", r"カフェ|喫茶|パン|ベーカリー|スイーツ|菓子|甘味|ジェラート|アイス|デザート|チョコレート|ショコラ|プラリネ"),
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


# ガイドの所在国の料理を指す見出しは「ご当地名物」にする。
# 「ベルギー料理・レストラン」はベルギーのガイドでは郷土料理だが、
# 日本のガイドに出てくれば外国料理である。**同じ語でも、どの国のガイドかで意味が変わる。**
# リエージュ・ケルンでは郷土料理の章を「ご当地名物」に対応させており、
# ルーベンだけこの規則から外れて「ご当地名物が0件」になっていた（2026-09-09 の指摘）。
HOME_CUISINE = {
    "belgium": r"ベルギー料理|フランデレン|フラマン",
    "germany": r"ドイツ料理",
    "france": r"フランス料理|ビストロ",
    "netherlands": r"オランダ料理",
    "nepal": r"ネパール料理",
    "usa": r"ハワイ|ローカルフード|ロコ",
}


def country_of_guide(guide):
    """ガイドの識別子から国のキーを拾う。

    `guide` は `north_america_usa_alamoana` のような**アンダースコア区切り**で、
    スラッシュ区切りではない（2026-09-19 実測。ここを取り違えると HOME_CUISINE が
    一度も当たらず、ハワイのご当地料理が「和食・郷土料理」に落ちる）。
    """
    g = (guide or "").lower()
    for k in HOME_CUISINE:
        if k in g:
            return k
    return ""


def categories_of(heading, country="", name="", dish="", desc=""):
    """その店のカテゴリを**複数**返す（主カテゴリが先頭）。

    **なぜ複数が要るか**: ユーザー指摘（2026-09-12）「ご当地グルメかつビールの店が、
    どちらかでしか出ない」。`category_of` は**最初に当たった規則で打ち切る**ので、
    1店1カテゴリしか持てなかった。

    **なぜ見出しだけで決められないか**: 見出しは
    「日本食・ラーメン・寿司・居酒屋」のように**複数ジャンルの束**であることがある。
    見出しの一致をそのまま全部採ると、うどん店に「寿司・海鮮」が付く（実測で確認）。
    そこで**候補は見出しから出し、採否は店自身の文（店名・一皿・説明）で裏を取る**。

    **順序**: 店自身の文の中で**早く出てくる語ほどその店の主題に近い**ので、
    一致位置の昇順に並べる。これで「握り寿司に…」の店が寿司・海鮮になり、
    「肉汁つけうどん…」の店が麺類になる（どちらも見出しは同じ束）。

    **所在国の郷土料理（HOME_CUISINE）は主カテゴリを動かさない**（B-464）。
    """
    home = HOME_CUISINE.get((country or "").lower())
    is_home = bool(home and re.search(home, heading))

    cand = []
    head = re.split(r"[・/／(（]", heading)[0]
    for target in (head, heading):
        for cat, pat in CATEGORY_RULES:
            if re.search(pat, target) and cat not in cand:
                cand.append(cat)

    own = " ".join([str(name or ""), str(dish or ""), str(desc or "")])
    rules = dict(CATEGORY_RULES)
    scored = []
    for cat in cand:
        pat = rules.get(cat)
        if not pat:
            continue
        hit = re.search(pat, own)
        if hit:
            scored.append((hit.start(), cat))
    scored.sort()
    ev = [c for _, c in scored]

    if is_home:
        return ["ご当地名物"] + [c for c in ev if c != "ご当地名物"]
    if len(cand) <= 1:
        return cand or [category_of(heading, country)]
    return ev if ev else [category_of(heading, country)]


def category_of(heading, country=""):
    """見出しをカテゴリへ畳む。

    見出しは「京料理・和食・寿司・鶏料理」のように複数ジャンルが並ぶので、
    **先頭の区切りまでを先に見る**（その節の主題は先頭にある）。
    先頭で決まらなければ見出し全体で当てる。
    """
    pat = HOME_CUISINE.get((country or "").lower())
    if pat and re.search(pat, heading):
        return "ご当地名物"
    head = re.split(r"[・/／(（]", heading)[0]
    for target in (head, heading):
        for name, pat in CATEGORY_RULES:
            if re.search(pat, target):
                return name
    return "和食・郷土料理"   # どれにも当たらない見出しの受け皿


def first_url(s):
    m = re.search(r"\((https?://[^)]+)\)", s)
    return m.group(1) if m else ""


# 日本のガイドの表紙は「JAPAN / GIFU・岐阜県 🇯🇵」の形だが、
# 大垣は「大垣市」、吹田は「北摂」、藤井寺は「南河内」と**県名ではない語**が入る
# （2026-09-19 実測）。都市一覧を県でまとめるには県名が要るので、
# ディレクトリ名（japan/<pref>/<city>.html）を正とする。
JP_PREF = {
    "aichi": "愛知県", "akita": "秋田県", "aomori": "青森県", "chiba": "千葉県",
    "ehime": "愛媛県", "fukui": "福井県", "fukuoka": "福岡県", "fukushima": "福島県",
    "gifu": "岐阜県", "gunma": "群馬県", "hiroshima": "広島県", "hokkaido": "北海道",
    "hyogo": "兵庫県", "ibaraki": "茨城県", "ishikawa": "石川県", "iwate": "岩手県",
    "kagawa": "香川県", "kagoshima": "鹿児島県", "kanagawa": "神奈川県", "kochi": "高知県",
    "kumamoto": "熊本県", "kyoto": "京都府", "mie": "三重県", "miyagi": "宮城県",
    "miyazaki": "宮崎県", "nagano": "長野県", "nagasaki": "長崎県", "nara": "奈良県",
    "niigata": "新潟県", "oita": "大分県", "okayama": "岡山県", "okinawa": "沖縄県",
    "osaka": "大阪府", "saga": "佐賀県", "saitama": "埼玉県", "shiga": "滋賀県",
    "shimane": "島根県", "shizuoka": "静岡県", "tochigi": "栃木県", "tokushima": "徳島県",
    "tokyo": "東京都", "tottori": "鳥取県", "toyama": "富山県", "wakayama": "和歌山県",
    "yamagata": "山形県", "yamaguchi": "山口県", "yamanashi": "山梨県",
}


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

    seg = path.replace("\\", "/").split("/")
    region = {"japan": "日本", "europe": "ヨーロッパ", "asia": "アジア",
              "north_america": "北米"}.get(seg[0], "")
    # 日本は表紙が「JAPAN / GIFU・岐阜県 🇯🇵」で「・」の右が県名。
    # 国外は「USA / HAWAII・ホノルル(ワイキキ) 🇺🇸」のように **「・」の右が都市名** で、
    # 県名ではない（2026-09-19 実測。ここを共通化していたのでハワイの「国」が
    # 「ホノルル(ワイキキ)」になり、都市一覧が国でまとまらなかった）。
    # したがって **「・」で取るのは日本だけ**、国外はディレクトリ名から国名を引く。
    pref = ""
    if region == "日本":
        pref = JP_PREF.get(seg[1] if len(seg) > 1 else "", "")
        if pref:
            pass
        elif "・" in head:
            pref = re.sub(r"\s*[\U0001F1E6-\U0001F1FF]{2}\s*$", "", head.split("・", 1)[1]).strip()
        else:
            # 京都・大阪は表紙が「JAPAN / KYOTO 🇯🇵」で府名が省かれている（都市名と同じため）
            pref = {"京都": "京都府", "大阪": "大阪府"}.get(city, "")
    else:
        country = {"belgium": "ベルギー", "france": "フランス", "germany": "ドイツ",
                   "netherlands": "オランダ", "nepal": "ネパール",
                   "usa": "アメリカ（ハワイ）"}
        pref = country.get(seg[1] if len(seg) > 1 else "", "")
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
            # 所在国のディレクトリ名（europe/belgium/leuven.html → "belgium"）。
            # 「その国の料理」を「ご当地名物」に畳むために使う（HOME_CUISINE）。
            parts = rel.split("/")
            country = parts[1] if len(parts) > 2 else ""

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
                    cats = categories_of(heading, country_of_guide(base) or country,
                                         c["name"], c["sig"], c["desc"])
                    rec = {
                        "guide": base, "guide_title": title, "path": rel,
                        "都市": city, "国・都道府県": pref, "地方": region,
                        "slug": cid,
                        "店名": c["name"], "よみ": c["yomi"],
                        "地図番号": int(c["no"]) if c["no"].isdigit() else None,
                        "章（原文）": heading, "カテゴリ": cats[0], "カテゴリ群": cats,
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
    multi = [r for r in out if len(r.get("カテゴリ群", [])) > 1]
    print("複数カテゴリ   : %d (%.0f%%)" % (len(multi), 100.0 * len(multi) / max(1, len(out))))
    empty = [r["guide"] for r in out if not r["都市"] or not r["国・都道府県"]]
    print("都市/県が空    : %d %s" % (len(empty), sorted(set(empty))[:5]))


if __name__ == "__main__":
    main()
