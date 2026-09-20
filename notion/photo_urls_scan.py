# -*- coding: utf-8 -*-
"""ページの**生HTML**から画像URLを拾う。

WebFetch は markdown へ変換する過程で、**遅延読み込みの画像を
`data:image/svg+xml` のプレースホルダーのまま返す**（2026-09-20 実測）ので使わない。
生HTML を取って `src` / `data-src` / `srcset` / `og:image` / JSON-LD の `image` を全部見る。
"""
import re, sys, json, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"}
SKIP = re.compile(r"(logo|icon|favicon|sprite|placeholder|avatar|banner|badge|flag|arrow|spinner|blank|pixel)", re.I)

def fetch(u, timeout=25):
    r = urllib.request.Request(u, headers=UA)
    d = urllib.request.urlopen(r, timeout=timeout).read()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return d.decode(enc)
        except Exception:
            pass
    return d.decode("utf-8", "replace")

def urls(page, base):
    out = []
    pats = [r'<img[^>]+?src=["\']([^"\']+)', r'data-src=["\']([^"\']+)',
            r'data-lazy-src=["\']([^"\']+)', r'srcset=["\']([^"\']+)',
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
            r'"image"\s*:\s*"([^"]+)"', r'"contentUrl"\s*:\s*"([^"]+)"',
            r'background-image:\s*url\(["\']?([^"\')]+)']
    for p in pats:
        for m in re.findall(p, page, re.I):
            for cand in re.split(r",\s*", m):
                u = cand.strip().split(" ")[0]
                if not u or u.startswith("data:"):
                    continue
                u = urllib.parse.urljoin(base, u)
                if not re.search(r"\.(jpe?g|png|webp)(\?|$)", u, re.I):
                    continue
                if SKIP.search(u):
                    continue
                if u not in out:
                    out.append(u)
    return out

if __name__ == "__main__":
    for u in sys.argv[1:]:
        try:
            p = fetch(u)
            got = urls(p, u)
            print("=== %s : %d 本" % (u, len(got)))
            for g in got[:12]:
                print("   ", g[:130])
        except Exception as e:
            print("=== %s : 失敗 %s" % (u, str(e)[:70]))
