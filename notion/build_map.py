# -*- coding: utf-8 -*-
"""全66都市の地図ページと、都市一覧（サイトの入口）を作る。

ユーザー依頼:
  2026-09-06「ポップアップと記事に料理の写真と店の外観の写真が欲しい。
              ピンにはどのカテゴリの店かわかるように色分けと、
              ポップアップには店の一言紹介が欲しい」
  2026-09-19「フィルター機能と一覧機能と目次も実装してくれ。都市一覧も作ってくれ」

色の決め方（dataviz スキルの手順に従った）:
  地図は「どの2つのピンも隣り合いうる」形式なので、色の検証は全ペア（--pairs all）で行う。
  検証スクリプトの実測で、既定の8色は全ペアだと落ちる
  （赤↔橙の通常視 ΔE 7.1・緑↔橙の色覚多様性 ΔE 3.2）。
  **全ペアで通るのは4色まで**（青 #2a78d6・橙 #eb6834・青緑 #1baf7a・菫 #4a3aa7、
  色覚多様性 ΔE 9.2・通常視 ΔE 16.3）。
  そこで **11カテゴリを4つの系統に束ね、系統を色、カテゴリを絵文字で表す。**
  ＝**識別は色だけに依存しない**（絞り込みチップにもカテゴリ名を出す）。
  地図の背景は常に明るいタイルなので、配色は明るい面用の1組に決め打ちする。

公開のしかた（2026-09-19 実測）:
  GitHub Pages の Source は「Deploy from a branch（main / root）」で、
  **リポジトリの中身がそのまま配信されている**（/notion/stores.json が 200 を返すことで確認）。
  つまり記事HTMLも写真も既に公開URLを持っているので、
  **地図から記事へ相対リンクで直接飛べる**し、公開用に _site を別に組む必要がない。
  そのため .github/workflows/map-pages.yml（_site を組んで actions/deploy-pages で出す）は
  削除した。**残しておくと push のたびに Pages の配信元を Actions 側へ切り替えてしまい、
  記事HTMLも写真も _site に入っていないので公開サイトが地図だけになる。**

出力: index.html（サイトの入口＝都市一覧）, map/index.html（同じ一覧）,
      map/<都市slug>.html（都市ごとの地図＋一覧）
"""
import json
import os
import shutil
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rwd import TOGGLE_CSS, TOGGLE_HTML, TOGGLE_JS, dual   # noqa: E402
from sitenav import BURGER, NAV_CSS, NAV_JS, menu_html, nav_html  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(ROOT, "notion", "stores.json")
SITE = os.path.join(ROOT, "map")

# 既定は全都市。CITIES を与えればその都市だけ作る（動作確認用）。
CITIES = [c for c in os.environ.get("CITIES", "").split(",") if c]

# 系統 → 色（dataviz の検証スクリプトで全ペア合格を確認した4色）
FAMILY_COLOR = {
    "麺類": "#2a78d6",
    "和食": "#eb6834",
    "洋食・アジア": "#1baf7a",
    "カフェ・酒場": "#4a3aa7",
}
# カテゴリ → (系統, 絵文字)。並び順がチップと目次の並び順になる。
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

# 地方の並び（日本→近い順）。ここに無い地方は末尾へ。
REGION_ORDER = ["日本", "アジア", "ヨーロッパ", "北米"]
# 都道府県は JIS X 0401 の順（北から）。一覧が地図の並びと合う。
PREF_ORDER = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]


def city_slug(store):
    """都市ページのファイル名。記事のファイル名をそのまま使う（66都市で重複なしを実測）。"""
    return os.path.basename(store["path"])[:-5]


def img_paths(s):
    """(料理, 外観) を (リポジトリ相対パス or None) で返す。

    写真は `<記事のディレクトリ>/img/<記事名>/<slug>.jpg` に置いてある。
    以前は `guide`（"north_america_usa_waikiki"）を "_" で割って組み立てていたが、
    アンダースコアを含むディレクトリ名（north_america）が復元できず、
    **ハワイ3都市の写真が1枚も出ていなかった**（2026-09-19 実測）。
    `path` は元の相対パスそのものなので、割らずに済む。
    """
    d, fn = os.path.split(s["path"])
    rel = "%s/img/%s" % (d, fn[:-5])
    food = "%s/%s.jpg" % (rel, s["slug"])
    ext = "%s/%s_exterior.jpg" % (rel, s["slug"])
    return (food if os.path.exists(os.path.join(ROOT, food)) else None,
            ext if os.path.exists(os.path.join(ROOT, ext)) else None)


CSS = """
  :root { color-scheme: light; --ink:#16150f; --ink2:#52514e; --line:#dcdbd4; --bg:#fcfcfb; --acc:#8a2b16; }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;font:14px/1.6 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;color:var(--ink);background:var(--bg)}
  a{color:var(--acc)}
  .bar{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;padding:8px 12px;border-bottom:1px solid var(--line);background:#fff}
  .bar h1{font-size:15px;margin:0;font-weight:600}
  .bar .n{font-weight:400;color:var(--ink2);font-size:12px;margin-left:6px}
  .bar nav{margin-left:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  button{font:inherit;border:1px solid var(--line);background:#fff;border-radius:8px;padding:3px 10px;cursor:pointer;color:inherit}
  button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .chips{display:flex;flex-wrap:wrap;gap:6px;padding:7px 12px;border-bottom:1px solid var(--line);background:#fff}
  .chip{display:inline-flex;align-items:center;gap:5px;font-size:12px;padding:2px 9px;border-radius:999px;
        border:1px solid var(--line);background:#fff;cursor:pointer}
  .chip[aria-pressed="false"]{opacity:.35}
  .chip b{font-weight:400;color:var(--ink2);font-variant-numeric:tabular-nums}
  .sw{width:10px;height:10px;border-radius:50%;flex:0 0 auto}
  main{position:relative;flex:1 1 auto;min-height:0}
  #map,#list{position:absolute;inset:0}
  #list{overflow:auto;display:none;background:var(--bg)}
  .pin{display:grid;place-items:center;width:26px;height:26px;border-radius:50%;
       box-shadow:0 0 0 2px #fff,0 1px 3px rgba(0,0,0,.35);font-size:14px}
  .leaflet-popup-content{margin:10px 12px;width:250px!important}
  .pop h3{margin:0 0 2px;font-size:15px}
  .pop .cat{font-size:12px;color:var(--ink2);margin:0 0 6px}
  .pop .dish{margin:0 0 8px}
  .pop figure{margin:0}
  .pop .imgs{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px}
  .pop img{width:100%;height:132px;object-fit:cover;border-radius:8px;display:block;background:#eee}
  .pop figcaption{font-size:11px;color:var(--ink2);margin-top:2px}
  .pop .links{margin:0}
  .pop .links a{margin-right:10px;font-size:12px}
  .lhead{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:8px 12px;z-index:2}
  .lhead input{font:inherit;width:100%;max-width:420px;padding:5px 10px;border:1px solid var(--line);border-radius:8px;background:#fff}
  .toc{display:flex;flex-wrap:wrap;gap:4px 12px;margin-top:7px;font-size:12px}
  .toc a{color:var(--ink2);text-decoration:none;white-space:nowrap}
  .toc a:hover{text-decoration:underline}
  .toc b{font-weight:400;color:#8b8a85;font-variant-numeric:tabular-nums}
  .grp{padding:0 12px}
  .grp h2{font-size:13px;margin:18px 0 6px;padding-bottom:4px;border-bottom:2px solid var(--line);
          display:flex;align-items:center;gap:6px;scroll-margin-top:64px}
  .grp h2 b{font-weight:400;color:var(--ink2);font-size:12px}
  table{border-collapse:collapse;width:100%}
  th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;font-size:13px;vertical-align:top}
  td.nm{font-weight:600;white-space:nowrap}
  td.ac{white-space:nowrap;text-align:right}
  td.ac a,td.ac button{font-size:12px;margin-left:8px}
  .empty{padding:24px 12px;color:var(--ink2)}
  .wrap{max-width:900px;margin:0 auto;padding:16px 16px 48px}
  .wrap h2{font-size:15px;margin:26px 0 2px;padding-top:12px;border-top:2px solid var(--line);scroll-margin-top:56px}
  .wrap h3{font-size:13px;color:var(--ink2);margin:14px 0 2px;font-weight:600}
  .lead{color:var(--ink2);margin:6px 0 0}
  .foot{color:var(--ink2);font-size:12px;margin-top:32px}
  ul.cities{list-style:none;margin:2px 0 0;padding:0}
  ul.cities li{display:flex;gap:10px;align-items:baseline;padding:4px 0;border-bottom:1px solid var(--line)}
  ul.cities .cn{font-weight:600;min-width:9em}
  ul.cities .cc{color:var(--ink2);font-size:12px;font-variant-numeric:tabular-nums;min-width:5em}
  ul.cities .cl{margin-left:auto;white-space:nowrap;font-size:12px}
  ul.cities .cl a{margin-left:10px}
""" + TOGGLE_CSS + NAV_CSS + """
  .bar{align-items:center}
""" + dual("""
  /* --- スマホ（画面幅 640px 以下、または「スマホ表示」に固定したとき） --------------
     狙いは3つ。①ヘッダと絞り込みが画面を食いすぎないようにする
     （実測＝390x844 の端末でヘッダ105px＋チップ134px＝239px＝画面の28%を占めていた）
     ②吹き出しの決め打ちの幅 250px を画面幅に追従させる
     ③一覧の4列の表を、1店1枚のカードに積み替える（列が窮屈で、指でも押しにくいため） */
  @@ .bar{padding:6px 10px;gap:6px;flex-wrap:nowrap}
  /* ☰ と見出しと（地図/一覧）を**1行に収める**。2026-09-19 の版は
     `h1{width:100%}` + `nav{width:100%}` で3行になり、ヘッダだけで画面の2割を食っていた
     （390x844 の実測）。見出しは足りなければ省略記号で詰める。 */
  @@ .bar h1{font-size:14px;width:auto;flex:1 1 auto;min-width:0;
             overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  @@ .bar .n{margin-left:4px}
  @@ .bar nav{margin-left:auto;width:auto;gap:6px;flex-wrap:nowrap;flex:0 0 auto}
  @@ .chips{padding:6px 10px;gap:5px;flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch}
  @@ .chip{flex:0 0 auto}
  @@ .leaflet-popup-content{width:min(74vw,250px)!important}
  @@ .pop img{height:104px}
  @@ .lhead input{max-width:none}

  /* 表 → カード。td を横に並べるのをやめ、1行ぶんを1枚の箱にする。 */
  @@ .grp table,@@ .grp tbody,@@ .grp tr,@@ .grp td{display:block;width:auto}
  @@ .grp tr{border:1px solid var(--line);border-radius:10px;background:#fff;
             padding:8px 10px;margin:0 0 8px}
  @@ .grp td{border:0;padding:2px 0}
  @@ .grp td.nm{white-space:normal;font-size:14px}
  @@ .grp td.ac{text-align:left;margin-top:4px}
  @@ .grp td.ac a,@@ .grp td.ac button{margin:0 12px 0 0}

  /* 都市一覧は、都市名・店数・リンクが折り返せるように積む。 */
  @@ ul.cities li{flex-wrap:wrap;gap:2px 10px}
  @@ ul.cities .cn{min-width:0}
  @@ ul.cities .cl{margin-left:auto}
  @@ .wrap{padding:12px 12px 40px}
""")

HEAD = """<!doctype html>
<html lang="ja">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
{{LEAFLET}}<style>{{CSS}}</style>
"""


def head(title, leaflet_css=""):
    return (HEAD.replace("{{TITLE}}", escape(title))
                .replace("{{LEAFLET}}", leaflet_css)
                .replace("{{CSS}}", CSS))


CITY_BODY = """<body style="display:flex;flex-direction:column">
<header class="bar">
  {{BURGER}}
  <h1>{{CITY}} の食べ歩き地図<span class="n">{{COUNTS}}</span></h1>
  <nav>
    <button id="b-map" class="on">地図</button>
    <button id="b-list">一覧</button>
  </nav>
</header>
{{MENU}}
<div class="chips" id="chips"></div>
<main>
  <div id="map"></div>
  <div id="list"></div>
</main>
<script src="vendor/leaflet.js"></script>
<script>
const COLOR={{COLORS}}, CAT={{CATMETA}}, DATA={{DATA}};
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---- カテゴリの絞り込み（既定は全部オン） ---------------------------------
   1店が複数カテゴリを持つ（例: ご当地名物かつビール・バー）。
   **どちらのカテゴリで絞っても出る**ように、積ではなく和で判定する。 */
const CATS=[];
for(const k in CAT){ if(DATA.some(r=>r.c.includes(k))) CATS.push(k); }
const on=new Set(CATS);
const chips=document.getElementById('chips');
chips.innerHTML=CATS.map(k=>{
  const n=DATA.filter(r=>r.c.includes(k)).length;
  return `<button class="chip" data-cat="${esc(k)}" aria-pressed="true">`+
         `<span class="sw" style="background:${COLOR[CAT[k][0]]}"></span>${CAT[k][1]} ${esc(k)} <b>${n}</b></button>`;
}).join('')+'<button class="chip" id="c-all" aria-pressed="true">すべて</button>';

/* ---- 地図 ---------------------------------------------------------------- */
const pts=DATA.filter(r=>r.lat!=null);
const map=L.map('map',{zoomControl:true}).setView([{{LAT}},{{LNG}}],14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
const marks={};
for(const r of pts){
  const fam=CAT[r.c[0]]?CAT[r.c[0]][0]:'カフェ・酒場', gly=CAT[r.c[0]]?CAT[r.c[0]][1]:'•';
  const icon=L.divIcon({className:'',iconSize:[26,26],iconAnchor:[13,13],popupAnchor:[0,-14],
    html:`<div class="pin" style="background:${COLOR[fam]}">${gly}</div>`});
  let h=`<div class="pop"><h3>${esc(r.n)}</h3><p class="cat">${gly} ${esc(r.c.join(' / '))}</p>`;
  if(r.d) h+=`<p class="dish">${esc(r.d)}</p>`;
  if(r.food||r.ext){
    h+='<div class="imgs">';
    if(r.food) h+=`<figure><img loading="lazy" src="${esc(r.food)}" alt="${esc(r.n)}の料理"><figcaption>料理</figcaption></figure>`;
    if(r.ext) h+=`<figure><img loading="lazy" src="${esc(r.ext)}" alt="${esc(r.n)}の外観"><figcaption>外観</figcaption></figure>`;
    h+='</div>';
  }
  h+=`<p class="links"><a href="${esc(r.u)}">記事で読む</a>`+
     (r.m?`<a href="${esc(r.m)}" target="_blank" rel="noopener">Googleマップ</a>`:'')+'</p></div>';
  const mk=L.marker([r.lat,r.lng],{icon:icon,title:r.n}).bindPopup(h);
  marks[r.i]=mk;
}
if(pts.length) map.fitBounds(L.featureGroup(Object.values(marks)).getBounds().pad(0.05));

/* ---- 一覧（カテゴリごと・目次つき・検索つき） ------------------------------- */
const list=document.getElementById('list');
list.innerHTML='<div class="lhead"><input id="q" type="search" placeholder="店名・一皿・住所で探す" '+
  'autocomplete="off"><div class="toc" id="toc"></div></div><div id="grps"></div>';
const q=document.getElementById('q'), toc=document.getElementById('toc'), grps=document.getElementById('grps');

function shown(){
  const t=q.value.trim().toLowerCase();
  return DATA.filter(r=>{
    if(!r.c.some(c=>on.has(c))) return false;
    if(!t) return true;
    return (r.n+' '+r.d+' '+r.a+' '+r.c.join(' ')).toLowerCase().includes(t);
  });
}
function render(){
  const rs=shown();
  /* 複数カテゴリの店は**そのすべての見出しに出す**（利用者はどちらからも探すため） */
  const parts=[], tocp=[];
  for(const k of CATS){
    if(!on.has(k)) continue;
    const rows=rs.filter(r=>r.c.includes(k));
    if(!rows.length) continue;
    const id='g-'+CATS.indexOf(k);
    tocp.push(`<a href="#${id}">${CAT[k][1]} ${esc(k)} <b>${rows.length}</b></a>`);
    parts.push(`<section class="grp"><h2 id="${id}"><span class="sw" style="background:${COLOR[CAT[k][0]]}"></span>`+
      `${CAT[k][1]} ${esc(k)} <b>${rows.length}店</b></h2><table><tbody>`+
      rows.map(r=>`<tr><td class="nm">${esc(r.n)}</td><td>${esc(r.d)}</td><td class="ac">`+
        (r.lat!=null?`<button data-go="${r.i}">地図</button>`:'<span style="color:#9a9995;font-size:12px">座標なし</span>')+
        `<a href="${esc(r.u)}">記事</a>`+
        (r.m?`<a href="${esc(r.m)}" target="_blank" rel="noopener">MAP</a>`:'')+
        `</td></tr>`).join('')+'</tbody></table></section>');
  }
  toc.innerHTML=tocp.join('');
  grps.innerHTML=parts.length?parts.join(''):'<p class="empty">条件に合う店がありません。</p>';
}

/* ---- 表示の切り替えと配線 -------------------------------------------------- */
const bMap=document.getElementById('b-map'), bList=document.getElementById('b-list');
function view(v){
  const m=v==='map';
  document.getElementById('map').style.display=m?'block':'none';
  list.style.display=m?'none':'block';
  bMap.classList.toggle('on',m); bList.classList.toggle('on',!m);
  if(m) map.invalidateSize();
}
bMap.onclick=()=>view('map'); bList.onclick=()=>view('list');

function refresh(){
  for(const r of pts){
    const has=r.c.some(c=>on.has(c)), mk=marks[r.i];
    if(has && !map.hasLayer(mk)) mk.addTo(map);
    if(!has && map.hasLayer(mk)) map.removeLayer(mk);
  }
  render();
}
chips.onclick=e=>{
  const b=e.target.closest('.chip'); if(!b) return;
  if(b.id==='c-all'){
    const all=on.size===CATS.length;
    on.clear(); if(!all) CATS.forEach(c=>on.add(c));
  }else{
    const k=b.dataset.cat;
    on.has(k)?on.delete(k):on.add(k);
  }
  for(const el of chips.querySelectorAll('.chip[data-cat]'))
    el.setAttribute('aria-pressed', on.has(el.dataset.cat)?'true':'false');
  document.getElementById('c-all').setAttribute('aria-pressed', on.size?'true':'false');
  refresh();
};
q.oninput=render;
grps.onclick=e=>{
  const b=e.target.closest('button[data-go]'); if(!b) return;
  const mk=marks[b.dataset.go]; if(!mk) return;
  view('map'); map.setView(mk.getLatLng(),17); mk.openPopup();
};
refresh(); view('map');
{{NAVJS}}
/* この都市を「直前に見た地図」として覚える（都市一覧の先頭ボタンがここへ戻る）。 */
window.__snRemember('{{SLUG}}', {{CITYJS}});
{{TOGGLEJS}}
</script>
"""


def city_page(city, stores, prefix="../", ncities=0):
    pts = [s for s in stores if s.get("lat") is not None and s.get("lng") is not None]
    lat = sum(s["lat"] for s in pts) / len(pts) if pts else 35.0
    lng = sum(s["lng"] for s in pts) / len(pts) if pts else 135.0
    data = []
    for i, s in enumerate(sorted(stores, key=lambda x: (x.get("地図番号") or 9999))):
        food, ext = img_paths(s)
        cats = s.get("カテゴリ群") or [s["カテゴリ"]]
        data.append({
            "i": i, "n": s["店名"], "c": cats,
            "lat": s.get("lat"), "lng": s.get("lng"),
            "d": s.get("一皿") or "", "a": s.get("住所") or "",
            "m": s.get("Googleマップ") or "",
            "u": prefix + s["path"] + ("#c-" + s["slug"] if s.get("slug") else ""),
            "food": (prefix + food) if food else "",
            "ext": (prefix + ext) if ext else "",
        })
    slug = city_slug(stores[0])
    counts = "%d店" % len(data)
    if len(pts) != len(data):
        counts += "（地図に出るのは %d店・残りは一覧に）" % len(pts)
    body = (CITY_BODY
            .replace("{{CITY}}", escape(city))
            .replace("{{COUNTS}}", escape(counts))
            .replace("{{GUIDE}}", escape(prefix + stores[0]["path"]))
            .replace("{{COLORS}}", json.dumps(FAMILY_COLOR, ensure_ascii=False))
            .replace("{{CATMETA}}", json.dumps(CATEGORY, ensure_ascii=False))
            .replace("{{DATA}}", json.dumps(data, ensure_ascii=False))
            .replace("{{LAT}}", "%f" % lat).replace("{{LNG}}", "%f" % lng)
            .replace("{{BURGER}}", BURGER)
            .replace("{{MENU}}", menu_html([
                ("この都市", None, ""),
                ("📄", "%sのガイド記事" % escape(city), escape(prefix + stores[0]["path"])),
                ("ほかの都市", None, ""),
                ("📖", "都市の一覧（%d都市）" % ncities, "index.html"),
                ("表示", None, ""),
                ("", "", TOGGLE_HTML),
            ], "%s の地図 メニュー" % escape(city)))
            .replace("{{SLUG}}", slug)
            .replace("{{CITYJS}}", json.dumps(city, ensure_ascii=False))
            .replace("{{NAVJS}}", NAV_JS)
            .replace("{{TOGGLE}}", TOGGLE_HTML).replace("{{TOGGLEJS}}", TOGGLE_JS))
    return head("%s の食べ歩き地図" % city,
                '<link rel="stylesheet" href="vendor/leaflet.css">\n') + body


def index_page(cities, prefix=""):
    """都市一覧。地方 → 国・都道府県 → 都市 の3段で、地図と記事の両方へ繋ぐ。

    `prefix` はリポジトリ直下から見た相対（""）か、map/ から見た相対（"../"）。
    地図ページへのリンクだけは `map/` の有無が逆になるので別に組む。
    """
    mapdir = "map/" if prefix == "" else ""
    tree = {}
    for c in cities:
        tree.setdefault(c["region"], {}).setdefault(c["pref"], []).append(c)

    def rkey(r):
        return (REGION_ORDER.index(r) if r in REGION_ORDER else len(REGION_ORDER), r)

    def pkey(p):
        return (PREF_ORDER.index(p) if p in PREF_ORDER else len(PREF_ORDER), p)

    nav, secs, mrows = [], [], []
    for r in sorted(tree, key=rkey):
        rid = "r-" + str(rkey(r)[0])
        n = sum(c["n"] for p in tree[r] for c in tree[r][p])
        nav.append('<a href="#%s">%s <b>%d都市 / %d店</b></a>'
                   % (rid, escape(r), sum(len(v) for v in tree[r].values()), n))
        mrows.append(("・", "%s（%d都市）" % (escape(r), sum(len(v) for v in tree[r].values())),
                      "#" + rid))
        secs.append('<h2 id="%s">%s</h2>' % (rid, escape(r)))
        for p in sorted(tree[r], key=pkey):
            secs.append("<h3>%s</h3><ul class=\"cities\">" % escape(p))
            for c in sorted(tree[r][p], key=lambda x: x["city"]):
                secs.append(
                    '<li data-k="%s"><span class="cn">%s</span>'
                    '<span class="cc">%d店</span>'
                    '<span class="cl"><a href="%s%s.html">地図</a>'
                    '<a href="%s%s">ガイド記事</a></span></li>'
                    % (escape("%s %s %s" % (r, p, c["city"])), escape(c["city"]),
                       c["n"], mapdir, c["slug"], prefix, escape(c["path"])))
            secs.append("</ul>")

    total = sum(c["n"] for c in cities)

    # 一覧の先頭に「地図へ行く」ボタンを置く（2026-09-20 依頼）。
    # **どの都市の地図か**という情報が一覧には無いので、地図ページ側で覚えた
    # 「直前に見た地図」へ向ける。覚えが無ければ都市の検索窓へ案内する。
    rows = [("地図を開く", None, ""),
            ("", "", '<a href="#" id="sn-lastm" style="display:none">'
                     '<span class="sn-e">🗺️</span><span class="sn-l"></span></a>'),
            ("", "", '<a href="#" id="sn-pick">'
                     '<span class="sn-e">🔎</span>都市を選んで地図を開く</a>'),
            ("地方へ移動", None, "")] + mrows + [
            ("表示", None, ""), ("", "", TOGGLE_HTML)]
    snav = nav_html("美食ガイド", "%d都市 / %d店" % (len(cities), total),
                    ['<a class="sn-btn" id="sn-last" href="#">🗺️ 地図を開く</a>'],
                    rows, "美食ガイド メニュー")

    return head("美食ガイド 都市一覧") + """<body>
<style>
/* 都市一覧は縦に長い頁。地図ページと同じ `html,body{height:100%%}` のままだと、
   **貼りつくバーの容れ物（body）が画面1枚ぶんしか無く、バーが本文と一緒に流れて消える**
   （実測＝3000px 送ると y=-2199）。一覧の2枚だけ高さの縛りを外す。 */
html,body{height:auto;min-height:100%%}
</style>
%(snav)s
<div class="wrap">
<p class="lead">都市ごとに、店をカテゴリで色分けした地図と、全店の一覧・ガイド記事があります。
地図のピンをタップすると料理と外観の写真、名物の一皿、記事とGoogleマップへのリンクが出ます。</p>
<div class="lhead" style="position:static;border:0;padding:12px 0 0">
  <input id="q" type="search" placeholder="都市・県・国で探す（例: 静岡、ベルギー）" autocomplete="off">
  <div class="toc">%(nav)s</div>
</div>
%(secs)s
<p class="foot">写真の出典: Google の店舗写真および Google ストリートビュー。地図タイル: OpenStreetMap contributors。</p>
</div>
<script>
const q=document.getElementById('q');
q.oninput=()=>{
  const t=q.value.trim().toLowerCase();
  for(const li of document.querySelectorAll('ul.cities li'))
    li.style.display=(!t||li.dataset.k.toLowerCase().includes(t))?'':'none';
  /* 中身が全部消えた県・地方の見出しも一緒に隠す（空の見出しだけが並ばないように） */
  for(const ul of document.querySelectorAll('ul.cities')){
    const any=[...ul.children].some(li=>li.style.display!=='none');
    ul.style.display=any?'':'none';
    if(ul.previousElementSibling&&ul.previousElementSibling.tagName==='H3')
      ul.previousElementSibling.style.display=any?'':'none';
  }
  for(const h2 of document.querySelectorAll('.wrap h2')){
    let any=false;
    for(let e=h2.nextElementSibling;e&&e.tagName!=='H2';e=e.nextElementSibling)
      if(e.tagName==='UL'&&e.style.display!=='none') any=true;
    h2.style.display=any?'':'none';
  }
};
%(navjs)s
/* 先頭の「地図を開く」を、直前に見た地図へ向ける。
   覚えが無い端末では、押すと検索窓へ移る（押して何も起きない状態を作らない）。 */
(function(){
  var MAPDIR=%(mapdir)s;
  var last=window.__snLast(), b=document.getElementById('sn-last'),
      m=document.getElementById('sn-lastm'), pick=document.getElementById('sn-pick');
  function toQ(e){
    e.preventDefault();
    var q=document.getElementById('q');
    if(q){ q.scrollIntoView({block:'center'}); q.focus(); }
  }
  if(last){
    var href=MAPDIR+last.s+'.html';
    b.href=href; b.textContent='🗺️ '+last.c+'の地図';
    m.href=href; m.style.display=''; m.querySelector('.sn-l').textContent=last.c+'の地図へ戻る';
  }else{
    b.addEventListener('click', toQ);
  }
  pick.addEventListener('click', toQ);
})();
%(togglejs)s
</script>
""" % {"nc": len(cities), "nt": total, "nav": "".join(nav), "secs": "".join(secs),
       "snav": snav, "mapdir": json.dumps(mapdir),
       # 既存の <script> の中へ入れるので、タグでは包まない（包むと </script> が二重になる）
       "navjs": NAV_JS, "toggle": TOGGLE_HTML, "togglejs": TOGGLE_JS}


def main():
    stores = json.load(open(STORES, encoding="utf-8"))
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE, exist_ok=True)
    # Leaflet は同梱する。外部CDNに依存させない（読めない環境で地図が真っ白になるため）
    shutil.copytree(os.path.join(ROOT, "notion", "vendor"), os.path.join(SITE, "vendor"))

    order, groups = [], {}
    for s in stores:
        c = s.get("都市")
        if not c:
            continue
        if c not in groups:
            groups[c] = []
            order.append(c)
        groups[c].append(s)

    cities = []
    for city in (CITIES or order):
        sub = groups.get(city)
        if not sub:
            print("該当なし:", city)
            continue
        slug = city_slug(sub[0])
        open(os.path.join(SITE, slug + ".html"), "w", encoding="utf-8").write(
            city_page(city, sub, ncities=len(CITIES or order)))
        cities.append({"city": city, "slug": slug, "n": len(sub),
                       "path": sub[0]["path"], "region": sub[0].get("地方") or "その他",
                       "pref": sub[0].get("国・都道府県") or "—",
                       "pts": sum(1 for s in sub if s.get("lat") is not None)})

    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(
        index_page(cities, prefix="../"))
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        index_page(cities, prefix=""))

    nomap = [c for c in cities if c["pts"] < c["n"]]
    print("都市 %d / 店 %d" % (len(cities), sum(c["n"] for c in cities)))
    print("座標が欠けた都市 %d: %s"
          % (len(nomap), ", ".join("%s(%d/%d)" % (c["city"], c["pts"], c["n"])
                                   for c in nomap) or "なし"))
    print("→", SITE, "/", os.path.join(ROOT, "index.html"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
