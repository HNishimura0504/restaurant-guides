# -*- coding: utf-8 -*-
"""**閉業した店**を記事から取り除く。

規約 §7 [2026-08-15]「**格付けリストは現存の保証にならず、必ず営業状態の照会が要る**」の後始末。
閉業が確認できた店は載せない（読者が行って閉まっている、が最も重い不具合）。

触るのは ①店カード ②目次のその店の行 の2か所だけ。そのあと `build_map.py` と
`stores_extract.py` を回し直せば、地図のピンと座標と件数が追随する。
ピンの通し番号も本文の出現順で振り直す。

使い方: python3 notion/remove_store.py <記事のパス> <sid> [<sid> …]
"""
import io, re, sys


def main():
    path, sids = sys.argv[1], sys.argv[2:]
    s = io.open(path, encoding="utf-8").read()
    for sid in sids:
        key = '<div class="card" id="c-%s">' % sid
        if key not in s:
            print("   カードが無い: %s" % sid)
            continue
        i = s.index(key)
        # カードは `</div></div>` で閉じる（body と card）。**入れ子を数えて端を取る。**
        depth, j = 0, i
        while True:
            m = re.compile(r"<div\b|</div>").search(s, j)
            if not m:
                sys.exit("カードの終わりが見つからない: %s" % sid)
            depth += 1 if m.group(0) == "<div" else -1
            j = m.end()
            if depth == 0:
                break
        s = s[:i].rstrip() + "\n" + s[j:].lstrip("\n")
        # 目次のその店の行を全部消す（地図ごとに目次があるので複数出る）
        n = len(re.findall(r'\n?\s*<a href="#c-%s">.*?</a>' % re.escape(sid), s, re.S))
        s = re.sub(r'\n?\s*<a href="#c-%s">.*?</a>' % re.escape(sid), "", s, flags=re.S)
        # 地図のピンのアンカーも消す（中身が空の <a>）
        s = re.sub(r'\n?\s*<a href="#c-%s" style="[^"]*"></a>' % re.escape(sid), "", s)
        print("   消した: %s（目次から %d 行）" % (sid, n))

    # 通し番号を本文の出現順で振り直す
    k = 0
    out = []
    for part in re.split(r'(<span class="pinno" style="background:[^;]+;">\d*</span>)', s):
        m = re.match(r'(<span class="pinno" style="background:[^;]+;">)\d*(</span>)', part)
        if m:
            k += 1
            out.append("%s%d%s" % (m.group(1), k, m.group(2)))
        else:
            out.append(part)
    s = "".join(out)
    total = s.count('<div class="card" id="c-')
    s = re.sub(r"(\d+)\s*店", lambda m: "%d店" % total, s, count=1)
    io.open(path, "w", encoding="utf-8").write(s)
    print("%-40s 残り %d 店（番号を振り直した）" % (path, total))


if __name__ == "__main__":
    main()
