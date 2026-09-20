# -*- coding: utf-8 -*-
"""全ページ共通の「上に貼りつく案内バー ＋ ☰ メニュー」。

ユーザー依頼（2026-09-20）「**地図から一覧に遷移することはできるけど、一覧ページから
地図ページに遷移することができないからページ先頭にそのボタンを作って。
それから|||みたいな、メニュー出すものがあるともっと使いやすいかも**」。

**直している実害（実測）**:

| ページ | 先頭の案内 | 地図へ行けるか |
|---|---|---|
| 都市一覧 `index.html` / `map/index.html` | **無い** | 都市の行まで探して初めて行ける |
| 都市地図 `map/<都市>.html` | ある（ヘッダ） | ― |
| ガイド記事 `japan/<県>/<都市>.html` | ある（`.gnav`）が**先頭だけ** | 記事は3000行超あり、**下まで読むと戻れない** |

つまり「一覧の側から地図へ行く道」が、**都市一覧には1本も無く、記事では先頭に戻らないと
使えない**。どちらも「**上に貼りつく（sticky）バー**」1つで同時に直る。

**なぜ `.gnav` を置き換えるか**: 既存の `.gnav` は `position:static` の平文リンク行なので、
スクロールすると消える。同じ場所に貼りつくバーを置くほうが、行が1本増えるより読みやすい。

**なぜ項目を ☰ の中に畳むか**: スマホ実測で、地図ページのヘッダは 105px＋チップ 134px ＝
画面の28%を占めていた（`rwd.py` の記録）。**常時見せるのは1タップで要る2つまで**にして、
残り（都市一覧・ガイド記事・表示切替）はメニューへ入れる。

**「直前に見た地図」**: 都市一覧には「どの都市の地図か」という情報が無いので、
**地図ページを開いた時に都市を `localStorage` へ覚えておき、一覧の先頭ボタンをその地図へ向ける**。
覚えが無い端末では、ボタンは都市の検索窓へ案内する（押して何も起きない状態を作らない）。
`localStorage` が読めない環境（プライベートブラウズ等）でも落ちないよう try/catch で囲む。

**印刷では消す**: ガイドは `@page{size:120mm 240mm}` の紙面向けなので `@media print` で隠す。
"""

# ---- 見た目 ---------------------------------------------------------------
# クラス名は全て `sn-` / `snav` で閉じる（66本のガイドはそれぞれ独自CSSを持つため、
# `.toc` `.links` `.cover` `.chip` のような既存の名前と当たらないようにする）。
NAV_CSS = """
.snav{position:sticky;top:0;z-index:1100;display:flex;align-items:center;gap:8px;
      padding:6px 10px;background:rgba(255,253,248,.96);backdrop-filter:blur(6px);
      border-bottom:1px solid #e4e2dc;color:#52514e;
      font:13px/1.6 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
.snav .sn-t{font-weight:600;color:#2f2e2b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.snav .sn-n{color:#8a8880;font-weight:400;font-size:12px;margin-left:6px;font-variant-numeric:tabular-nums}
.snav .sn-r{margin-left:auto;display:flex;align-items:center;gap:6px;flex:0 0 auto}
.sn-btn{display:inline-flex;align-items:center;gap:5px;font:inherit;font-size:12.5px;
        border:1px solid #dcdbd4;background:#fff;color:#8a2b16;border-radius:999px;
        padding:4px 12px;min-height:30px;cursor:pointer;text-decoration:none;white-space:nowrap}
.sn-btn:hover{border-color:#8a2b16}
.sn-bg{display:inline-flex;flex-direction:column;justify-content:center;gap:3.5px;
       width:36px;height:30px;padding:0 9px;flex:0 0 auto;
       border:1px solid #dcdbd4;background:#fff;border-radius:8px;cursor:pointer}
.sn-bg i{display:block;height:2px;background:#52514e;border-radius:1px}
.sn-bg:hover{border-color:#8a8880}
/* Leaflet の操作部品（ズームの＋−）は z-index 800、吹き出しは 700。
   メニューを 70 に置くと**地図ページで＋−が引き出しの上に描かれる**（実測）ので、
   バーと引き出しは Leaflet より上の段に置く。 */
.snavm{position:fixed;inset:0;z-index:1200;display:none}
.snavm.on{display:block}
.snavm .sn-ov{position:absolute;inset:0;background:rgba(20,18,14,.3)}
.snavm .sn-p{position:absolute;top:0;left:0;width:min(80vw,310px);height:100%;overflow:auto;
             background:#fffdf8;box-shadow:2px 0 18px rgba(0,0,0,.2);
             padding:8px 0 24px;
             font:14px/1.6 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
.snavm .sn-h{display:flex;align-items:center;padding:6px 14px 10px;border-bottom:1px solid #e4e2dc;
             color:#8a8880;font-size:12px}
.snavm .sn-x{margin-left:auto;border:0;background:none;font:inherit;font-size:20px;
             line-height:1;color:#8a8880;cursor:pointer;padding:0 4px}
.snavm a,.snavm .sn-i{display:flex;align-items:center;gap:10px;width:100%;box-sizing:border-box;
             padding:12px 16px;border:0;background:none;text-align:left;font:inherit;
             color:#2f2e2b;text-decoration:none;cursor:pointer}
.snavm a:hover,.snavm .sn-i:hover{background:#f3efe6}
.snavm .sn-e{width:1.4em;text-align:center;flex:0 0 auto}
.snavm .sn-s{padding:14px 16px 4px;color:#8a8880;font-size:11.5px;letter-spacing:.04em}
/* 表示切替は「行」ではなく**ボタンそのもの**を押させる。行側に pointer-events:none を
   置くと、`TOGGLE_JS` の `e.target.closest('.vmsw')` が null になり**押しても何も
   起きない**（ヘッドレスの実機テストで踏んだ）。行の代わりにボタンを幅いっぱいにする。 */
.snavm .sn-i{padding:8px 16px}
.snavm .sn-i .vmsw{width:100%;justify-content:center;padding:9px 12px;border-radius:8px}
/* 見出しや店カードへ飛んだとき、**貼りつくバーの下に隠れない**ようにする。
   `scroll-margin-top` は錨（#…）へ飛ぶときだけ効くので、他の見た目には触らない。
   バーの高さは実測 43px なので、少し余らせて 54px にする。 */
[id]{scroll-margin-top:54px}
@media print{.snav,.snavm{display:none!important}}
"""

# ---- 動き -----------------------------------------------------------------
# ・☰ で開閉。背景・×・Esc・項目のタップで閉じる。
# ・開いている間は背後を固定する（body の overflow）。
# ・地図ページでは「直前に見た地図」を覚える（都市一覧の先頭ボタンが向く先）。
NAV_JS = """
(function(){
  var K='rg-last-map';
  window.__snRemember=function(slug,city){
    try{ localStorage.setItem(K, JSON.stringify({s:slug,c:city})); }catch(e){}
  };
  window.__snLast=function(){
    try{ var v=JSON.parse(localStorage.getItem(K)||'null');
         return (v&&v.s)?v:null; }catch(e){ return null; }
  };
  function menu(){ return document.querySelector('.snavm'); }
  function open(v){
    var m=menu(); if(!m) return;
    m.classList.toggle('on', v);
    document.body.style.overflow = v ? 'hidden' : '';
    var b=document.querySelector('.sn-bg');
    if(b) b.setAttribute('aria-expanded', v?'true':'false');
  }
  document.addEventListener('click', function(e){
    var t=e.target;
    if(!t.closest) return;
    if(t.closest('.sn-bg')){ e.preventDefault(); open(!menu().classList.contains('on')); return; }
    if(t.closest('.sn-ov')||t.closest('.sn-x')){ open(false); return; }
    /* 表示切替は menu を開いたまま（切替結果をその場で見せる）。他の項目は閉じる。 */
    if(t.closest('.snavm') && !t.closest('.vmsw')) open(false);
  });
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') open(false); });
})();
"""


def _items(rows):
    """メニューの中身。rows は ("見出し", None) か (絵文字, 文字, href|生HTML)。"""
    out = []
    for r in rows:
        if r[1] is None:
            out.append('<div class="sn-s">%s</div>' % r[0])
        elif r[2].startswith("<a"):
            out.append(r[2])
        elif r[2].startswith("<"):
            out.append('<div class="sn-i">%s</div>' % r[2])
        else:
            out.append('<a href="%s"><span class="sn-e">%s</span>%s</a>'
                       % (r[2], r[0], r[1]))
    return "".join(out)


BURGER = ('<button type="button" class="sn-bg" aria-label="メニュー" aria-expanded="false">'
          "<i></i><i></i><i></i></button>")


def menu_html(rows, menu_title="メニュー"):
    """☰ で開く引き出し1枚。バーを持たないページ（地図ページ）でも使う。"""
    return ('<div class="snavm" role="dialog" aria-label="%(mt)s">'
            '<div class="sn-ov"></div>'
            '<nav class="sn-p">'
            '<div class="sn-h">%(mt)s'
            '<button type="button" class="sn-x" aria-label="閉じる">&times;</button></div>'
            '%(i)s'
            '</nav></div>' % {"i": _items(rows), "mt": menu_title})


def nav_html(title, count, buttons, rows, menu_title="メニュー"):
    """貼りつくバー1本と、その中身のメニュー1枚を組む。

    `buttons` は常時見せる（1タップで要る）もの。`rows` は ☰ の中。
    """
    return (
        '<div class="snav">' + BURGER +
        '<span class="sn-t">%(t)s%(n)s</span>'
        '<span class="sn-r">%(b)s</span>'
        '</div>'
        % {"t": title,
           "n": ('<span class="sn-n">%s</span>' % count) if count else "",
           "b": "".join(buttons)}) + menu_html(rows, menu_title)
