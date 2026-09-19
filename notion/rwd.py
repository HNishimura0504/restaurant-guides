# -*- coding: utf-8 -*-
"""端末に応じた2パターン表示（PC/タブレット と スマホ）の共有部品。

ユーザー依頼（2026-09-19）「**閲覧してるデバイスがpc/タブレットかスマホかを判別して、
pc/タブレットモードとスマホモード2パターンで表示されるようにできる？**」
→ 方式は本人が「**レスポンシブ＋手動切替**」を選択（`docs/requirements_responsive_2026.md`）。

**なぜ UA（User-Agent）で判別しないか**: **iPadOS の Safari は既定で「デスクトップ用サイト」を
名乗り、UA が Macintosh になる**ので、**UA だけでタブレットとPCを分けることは原理的にできない**。
判定は **画面の幅**という観測可能な量で行い、**外れたときの逃げ道として手動の切替を置く**。

**3つの状態**:

| モード | viewport | スマホ用のCSS |
|---|---|---|
| `auto`（既定） | `width=device-width` | 画面幅 640px 以下で当たる |
| `phone`（スマホ表示に固定） | `width=device-width` | 幅に関係なく当たる |
| `pc`（PC表示に固定） | **`width=1100`** | 当たらない |

`pc` で **viewport の幅を 1100px に固定する**のが要点。`width=device-width` のままでは
スマホの 390px に PC 用のCSSを当てることになり、ただ窮屈になるだけで「PC表示」にならない。
**幅を宣言して、利用者に拡大・スクロールしてもらう**のが、紙面をそのまま見せる唯一の方法。

**スマホ用のCSSを2回出す理由**: CSS には「メディアクエリの中で、ある状態のときだけ無効にする」を
1回で書く方法が無い。そこで**同じ規則を2か所へ出す**＝
①`@media screen and (max-width:640px){ html:not(.vm-pc) … }`（自動＋PC固定の打ち消し）
②`@media screen{ html.vm-phone … }`（スマホ固定）。**本文は1か所で書き、機械が2回展開する**ので食い違わない。
**どちらにも `screen` を付ける**＝付けないと `@page{size:120mm}`（≒453px）の**印刷にも当たってしまう**。
"""

# 切替ボタンの見た目。記事にも地図にも同じものを差し込む。
TOGGLE_CSS = """
.vmsw{display:inline-flex;align-items:center;gap:4px;font:inherit;font-size:12px;
      border:1px solid #dcdbd4;background:#fff;color:#52514e;border-radius:999px;
      padding:2px 10px;cursor:pointer;line-height:1.6;white-space:nowrap}
.vmsw:hover{border-color:#8a8880}
@media print{.vmsw{display:none}}
"""

# 切替の本体。
#  ・`localStorage` に覚える（この端末だけ・この配信元だけ）。
#  ・読めない環境（プライベートブラウズ等）でも落ちないように try/catch で囲む。
#  ・viewport メタが無いページでも動くよう、無ければ作る。
TOGGLE_JS = """
(function(){
  var K='rg-view-mode', order=['auto','phone','pc'];
  var label={auto:'\\u8868\\u793a: \\u81ea\\u52d5', phone:'\\u8868\\u793a: \\u30b9\\u30de\\u30db', pc:'\\u8868\\u793a: PC'};
  function get(){ try{ var v=localStorage.getItem(K); return order.indexOf(v)>=0?v:'auto'; }catch(e){ return 'auto'; } }
  function set(v){ try{ localStorage.setItem(K,v); }catch(e){} }
  function vp(){
    var m=document.querySelector('meta[name=viewport]');
    if(!m){ m=document.createElement('meta'); m.name='viewport'; document.head.appendChild(m); }
    return m;
  }
  function apply(v){
    var h=document.documentElement;
    h.classList.remove('vm-phone','vm-pc');
    if(v==='phone') h.classList.add('vm-phone');
    if(v==='pc') h.classList.add('vm-pc');
    vp().setAttribute('content', v==='pc' ? 'width=1100' : 'width=device-width, initial-scale=1');
    var b=document.querySelector('.vmsw');
    if(b){ b.textContent=label[v]; b.setAttribute('aria-label', label[v]+'\\uff08\\u62bc\\u3059\\u3068\\u5207\\u308a\\u66ff\\u308f\\u308a\\u307e\\u3059\\uff09'); }
  }
  window.__rgApply=apply;
  apply(get());
  document.addEventListener('click', function(e){
    var b=e.target.closest ? e.target.closest('.vmsw') : null;
    if(!b) return;
    var v=order[(order.indexOf(get())+1)%order.length];
    set(v); apply(v);
  });
})();
"""

TOGGLE_HTML = '<button type="button" class="vmsw">表示: 自動</button>'


def dual(rules):
    """スマホ用の規則を、①メディアクエリ ②スマホ固定 の2か所へ展開する。

    `rules` の中の `@@` を、その場に応じた前置きのセレクタへ置き換える。
    """
    a = rules.replace("@@", "html:not(.vm-pc)")
    b = rules.replace("@@", "html.vm-phone")
    # **`screen` を必ず付ける。** ガイドは `@page{size:120mm 240mm}` の紙面向けで、
    # 120mm ≒ 453px。`@media (max-width:640px)` だけだと **印刷にも当たってしまい**、
    # 紙面の文字サイズと目次の段組みが崩れる（実測で確認）。
    return ("@media screen and (max-width:640px){\n%s\n}\n"
            "@media screen{\n%s\n}\n" % (a, b))
