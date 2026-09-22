# -*- coding: utf-8 -*-
"""目次の「小さい灰色の一言」が、店名の繰り返しになっている行と、無い行を直す。

`toc_names.py` は、目次のリンク文字列を「店名」と「一言」に分ける。
ところが**元の目次が既に店名だけだった記事**では分けるものが無く、
`tsub`（一言）に元の文字列（番号＋店名）がそのまま入って、
画面には店名が2行続けて出ていた。8冊・535行。

直し方＝**一言をカードから取り直す。** カードの `<div class="sig"><b>一皿:</b>…</div>` が
「名物（説明）」の形なので、括弧の中を一言に使う。括弧が無ければ一皿の名前そのもの。
一皿が無ければ `tsub` ごと消す（空の行を残さない）。

使い方: python3 fix_tsub.py <記事のパス> [--dry-run]
"""
import html, io, re, sys

# `tsub` が【在って店名の繰り返し】の行と、【そもそも無い】行の両方を拾う。
ROW = re.compile(r'(<a href="#c-([^"]+)">.*?<span class="tnm">)(.*?)(</span>)(<span class="tsub">(.*?)</span>)?', re.S)
SIG = re.compile(r'<div class="card" id="c-%s">.*?<div class="sig"><b>一皿:</b>(.*?)</div>', re.S)


def one_liner(card_sig):
    t = card_sig.strip()
    m = re.search(r'[（(]([^（()）]+)[)）]\s*$', t)
    if m:
        return m.group(1).strip()
    return re.sub(r'\s*[（(].*$', '', t).strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if "--trim" in sys.argv:
        for a in args:
            trim_file(a, dry)
        return
    path = args[0]
    s = io.open(path, encoding="utf-8").read()
    fixed = dropped = kept = 0

    def rep(m):
        nonlocal fixed, dropped, kept
        head, sid, nm, tail, whole, sub = m.groups()
        sub = sub or ""
        # `&amp;amp;` のように二重エスケープされている行があるので、
        # 比べる前に両方とも実体参照を解いてから突き合わせる。
        # 先頭の番号は「消してから比べる」のではなく「番号＋店名」の形かどうかで見る。
        # 店名が数字で始まる店（808 Grindz Cafe）で、番号ごと食い合うため。
        sub_plain = html.unescape(html.unescape(sub)).strip()
        nm_plain = html.unescape(html.unescape(nm)).strip()
        dup = bool(re.fullmatch(r"\d*\s*" + re.escape(nm_plain), sub_plain))
        plain = "" if dup else sub_plain
        if plain and plain != nm_plain:
            kept += 1
            return m.group(0)                      # 正しい行は触らない
        g = SIG.search(s, 0)
        g = re.search(r'<div class="card" id="c-%s">.*?<div class="sig"><b>一皿:</b>(.*?)</div>'
                      % re.escape(sid), s, re.S)
        if not g:
            dropped += 1
            return head + nm + tail                # 一言が作れないなら span ごと消す
        line = one_liner(g.group(1))
        if not line:
            dropped += 1
            return head + nm + tail
        fixed += 1
        return head + nm + tail + '<span class="tsub">%s</span>' % line

    s2 = ROW.sub(rep, s)
    print("%-52s 直した %d / 一言が作れず消した %d / もとから正しい %d"
          % (path, fixed, dropped, kept))
    if not dry and s2 != s:
        io.open(path, "w", encoding="utf-8").write(s2)




# --- 一言の長さを1行に収める（2026-09-22） ---------------------------------
#
# 目次の一言は 7.4pt、段は 540 CSS px、左の字下げが 5.8mm なので、
# 1行に入るのは**全角でおよそ26字**。これを超えると2〜3行に折り返して、
# 「店名の下に小さく」という形が崩れる。実測で 30字超が 419 行あった。
#
# 切り方＝まず最初の句点で切る。それでも長ければ 26字で切って「…」を付ける。
# 使い方: python3 notion/fix_toc_subtitle.py --trim <記事のパス> […]

MAX = 26


def trim(text):
    t = html.unescape(text).strip()
    if len(t) <= MAX:
        return None
    head = t.split("。")[0].strip()
    if head and len(head) <= MAX + 4:
        out = head
    else:
        out = t[:MAX].rstrip("、（(・") + "…"
    return html.escape(out, quote=False)


def trim_file(path, dry=False):
    s = io.open(path, encoding="utf-8").read()
    n = [0]

    def rep(m):
        new = trim(m.group(1))
        if new is None:
            return m.group(0)
        n[0] += 1
        return '<span class="tsub">%s</span>' % new

    s2 = re.sub(r'<span class="tsub">(.*?)</span>', rep, s, flags=re.S)
    print("%-52s 1行に収めた %d" % (path, n[0]))
    if not dry and s2 != s:
        io.open(path, "w", encoding="utf-8").write(s2)


if __name__ == "__main__":
    main()
