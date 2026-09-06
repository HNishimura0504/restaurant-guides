# -*- coding: utf-8 -*-
"""都市ごとの地図ページを作る（カテゴリで色分け・写真2枚・一言紹介つき）。

ユーザー依頼（2026-09-06）:
  「ポップアップと記事に料理の写真と店の外観の写真が欲しい。
    ピンにはどのカテゴリの店かわかるように色分けと、ポップアップには店の一言紹介が欲しい」

色の決め方（dataviz スキルの手順に従った）:
  地図は「どの2つのピンも隣り合いうる」形式なので、色の検証は全ペア（--pairs all）で行う。
  検証スクリプトの実測で、既定の8色は全ペアだと落ちる
  （赤↔橙の通常視 ΔE 7.1・緑↔橙の色覚多様性 ΔE 3.2）。
  **全ペアで通るのは4色まで**（青 #2a78d6・橙 #eb6834・青緑 #1baf7a・菫 #4a3aa7、
  色覚多様性 ΔE 9.2・通常視 ΔE 16.3）。
  そこで **11カテゴリを4つの系統に束ね、系統を色、カテゴリを絵文字で表す。**
  ＝**識別は色だけに依存しない**（凡例・吹き出しにもカテゴリ名を出す）。
  地図の背景は常に明るいタイルなので、配色は明るい面用の1組に決め打ちする。

出力: site/index.html, site/<slug>.html, site/img/*.jpg
"""
import json
import os
import shutil
import sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
SITE = os.path.join(ROOT, "site")

CITIES = [c for c in os.environ.get(
    "CITIES", "大阪,京都,吹田,東京23区,ルーベン").split(",") if c]

# 系統 → 色（dataviz の検証スクリプトで全ペア合格を確認した4色）
FAMILY_COLOR = {
    "麺類": "#2a78d6",
    "和食": "#eb6834",
    "洋食・アジア": "#1baf7a",
    "カフェ・酒場": "#4a3aa7",
}
# カテゴリ → (系統, 絵文字)
CATEGORY = {
    "麺類": ("麺類", "🍜"),
    "和食・郷土料理": ("和食", "🍱"),
    "寿司・海鮮": ("和食", "🍣"),
    "ご当地名物": ("和食", "🎏"),
    "洋食・各国料理": ("洋食・アジア", "🍝"),
    "アジア・エスニック": ("洋食・アジア", "🍛"),
    "カフェ・パン・スイーツ": ("カフェ・酒場", "☕"),
    "居酒屋・焼肉": ("カフェ・酒場", "🍺"),
    "ビール・バー": ("カフェ・酒場", "🍻"),
    "屋台・食べ歩き": ("カフェ・酒場", "🍢"),
    "市場・食材店": ("カフェ・酒場", "🛒"),
}

CITY_SLUG = {"大阪": "osaka", "京都": "kyoto", "吹田": "suita",
             "東京23区": "tokyo23", "ルーベン": "leuven"}


def img_paths(s):
    p = s["guide"].split("_")
    d = os.path.join(ROOT, p[0], p[1], "img", p[2])
    food = os.path.join(d, s["slug"] + ".jpg")
    ext = os.path.join(d, s["slug"] + "_exterior.jpg")
    return (food if os.path.exists(food) else None,
            ext if os.path.exists(ext) else None)


HEAD = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<link rel="stylesheet" href="vendor/leaflet.css">
<style>
  :root { color-scheme: light; --ink:#16150f; --ink2:#52514e; --line:#dcdbd4; --bg:#fcfcfb; }
  html,body{margin:0;height:100%%;font:14px/1.6 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;color:var(--ink);background:var(--bg)}
  #map{position:absolute;inset:0}
  .bar{position:absolute;z-index:1000;top:8px;left:8px;right:8px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;
       background:rgba(252,252,251,.95);border:1px solid var(--line);border-radius:10px;padding:8px 10px}
  .bar h1{font-size:15px;margin:0 6px 0 0}
  .bar a{color:var(--ink2)}
  .legend{position:absolute;z-index:1000;left:8px;bottom:8px;background:rgba(252,252,251,.95);
          border:1px solid var(--line);border-radius:10px;padding:8px 10px;max-width:min(92vw,420px)}
  .legend b{display:block;font-size:12px;color:var(--ink2);font-weight:600;margin-bottom:4px}
  .legend ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 10px}
  .legend li{display:flex;align-items:center;gap:4px;font-size:12px;white-space:nowrap}
  .sw{width:12px;height:12px;border-radius:50%%;box-shadow:0 0 0 2px #fff}
  .pin{display:grid;place-items:center;width:26px;height:26px;border-radius:50%%;
       box-shadow:0 0 0 2px #fff,0 1px 3px rgba(0,0,0,.35);font-size:14px}
  .leaflet-popup-content{margin:10px 12px;width:250px!important}
  .pop h3{margin:0 0 2px;font-size:15px}
  .pop .cat{font-size:12px;color:var(--ink2);margin:0 0 6px}
  .pop .dish{margin:0 0 8px}
  .pop figure{margin:0 0 6px}
  .pop .imgs{display:grid;grid-template-columns:1fr 1fr;gap:6px}
  .pop img{width:100%%;height:132px;object-fit:cover;border-radius:8px;display:block;background:#eee}
  .pop figcaption{font-size:11px;color:var(--ink2);margin-top:2px}
  .pop .links a{margin-right:10px}
  table{border-collapse:collapse;width:100%%;background:var(--bg)}
  th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;font-size:13px;vertical-align:top}
  #list{position:absolute;inset:0;overflow:auto;background:var(--bg);padding:64px 12px 24px;display:none}
  button{font:inherit;border:1px solid var(--line);background:#fff;border-radius:8px;padding:4px 10px;cursor:pointer}
</style>
"""


def city_page(city, stores):
    pts = [s for s in stores if "lat" in s and "lng" in s]
    lat = sum(s["lat"] for s in pts) / len(pts)
    lng = sum(s["lng"] for s in pts) / len(pts)
    data = []
    for s in pts:
        fam, gly = CATEGORY.get(s["カテゴリ"], ("カフェ・酒場", "•"))
        food, ext = img_paths(s)
        rec = {
            "n": s["店名"], "c": s["カテゴリ"], "f": fam, "g": gly,
            "lat": s["lat"], "lng": s["lng"],
            "d": s.get("一皿") or "", "a": s.get("住所") or "",
            "m": s.get("Googleマップ") or "",
            "food": os.path.basename(food) if food else "",
            "ext": os.path.basename(ext) if ext else "",
        }
        data.append(rec)
    legend = "".join(
        '<li><span class="sw" style="background:%s"></span>%s %s</li>'
        % (FAMILY_COLOR[CATEGORY[c][0]], CATEGORY[c][1], escape(c))
        for c in CATEGORY)
    rows = "".join(
        "<tr><td>%s %s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (r["g"], escape(r["n"]), escape(r["c"]), escape(r["d"]),
           '<a href="%s">地図</a>' % escape(r["m"]) if r["m"] else "")
        for r in data)
    return (HEAD % {"title": "%s の食べ歩き地図" % city}) + """
<div class="bar">
  <h1>%(city)s の食べ歩き地図（%(n)d店）</h1>
  <button id="toggle">一覧で見る</button>
  <a href="index.html">ほかの都市</a>
</div>
<div id="map"></div>
<div id="list"><table><thead><tr><th>店</th><th>カテゴリ</th><th>一皿</th><th></th></tr></thead><tbody>%(rows)s</tbody></table></div>
<div class="legend"><b>色は系統・絵文字はカテゴリ</b><ul>%(legend)s</ul></div>
<script src="vendor/leaflet.js"></script>
<script>
const COLOR=%(colors)s, DATA=%(data)s;
const map=L.map('map').setView([%(lat)f,%(lng)f],14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const group=[];
for(const r of DATA){
  const icon=L.divIcon({className:'',iconSize:[26,26],iconAnchor:[13,13],popupAnchor:[0,-14],
    html:`<div class="pin" style="background:${COLOR[r.f]}">${r.g}</div>`});
  let html=`<div class="pop"><h3>${esc(r.n)}</h3><p class="cat">${r.g} ${esc(r.c)}</p>`;
  if(r.d) html+=`<p class="dish">${esc(r.d)}</p>`;
  if(r.food||r.ext){
    html+='<div class="imgs">';
    if(r.food) html+=`<figure><img loading="lazy" src="img/${r.food}" alt="${esc(r.n)}の料理"><figcaption>料理</figcaption></figure>`;
    if(r.ext) html+=`<figure><img loading="lazy" src="img/${r.ext}" alt="${esc(r.n)}の外観"><figcaption>外観</figcaption></figure>`;
    html+='</div>';
  }
  html+=`<p class="links">${r.m?`<a href="${esc(r.m)}" target="_blank" rel="noopener">Googleマップ</a>`:''}</p></div>`;
  const mk=L.marker([r.lat,r.lng],{icon:icon,title:r.n}).bindPopup(html);
  mk.addTo(map); group.push(mk);
}
map.fitBounds(L.featureGroup(group).getBounds().pad(0.05));
const btn=document.getElementById('toggle'), list=document.getElementById('list');
btn.onclick=()=>{const on=list.style.display!=='block';
  list.style.display=on?'block':'none';btn.textContent=on?'地図で見る':'一覧で見る';};
</script>
""" % {"city": escape(city), "n": len(data), "rows": rows, "legend": legend,
       "colors": json.dumps(FAMILY_COLOR, ensure_ascii=False),
       "data": json.dumps(data, ensure_ascii=False),
       "lat": lat, "lng": lng}


def main():
    stores = json.load(open(STORES, encoding="utf-8"))
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    # Leaflet は同梱する。外部CDNに依存させない（読めない環境で地図が真っ白になるため）
    shutil.copytree(os.path.join(ROOT, "notion", "vendor"),
                    os.path.join(SITE, "vendor"))
    links = []
    for city in CITIES:
        sub = [s for s in stores if s.get("都市") == city]
        if not sub:
            print("該当なし:", city)
            continue
        slug = CITY_SLUG.get(city, city)
        nfood = next_ext = 0
        for s in sub:
            food, ext = img_paths(s)
            if food:
                shutil.copyfile(food, os.path.join(SITE, "img", os.path.basename(food)))
                nfood += 1
            if ext:
                shutil.copyfile(ext, os.path.join(SITE, "img", os.path.basename(ext)))
                next_ext += 1
        open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
            city_page(city, sub))
        links.append((city, slug, len(sub), nfood, next_ext))
        print("%-8s %d店 / 料理%d / 外観%d" % (city, len(sub), nfood, next_ext))

    idx = (HEAD % {"title": "美食ガイドの地図"}) + """
<div style="max-width:640px;margin:32px auto;padding:0 16px">
<h1 style="font-size:20px">美食ガイドの地図</h1>
<p>ピンの色は料理の系統、絵文字はカテゴリです。ピンをタップすると料理と外観の写真、名物の一皿、Googleマップへのリンクが出ます。</p>
<table><thead><tr><th>都市</th><th>店数</th><th>料理写真</th><th>外観写真</th></tr></thead><tbody>
%s
</tbody></table>
<p style="color:var(--ink2);font-size:12px">写真の出典: Google の店舗写真および Google Street View。地図: OpenStreetMap</p>
</div>
""" % "".join('<tr><td><a href="%s.html">%s</a></td><td>%d</td><td>%d</td><td>%d</td></tr>'
              % (sl, escape(c), n, f, e) for c, sl, n, f, e in links)
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(idx)
    print("→", SITE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
