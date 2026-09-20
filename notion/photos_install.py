# -*- coding: utf-8 -*-
"""収集した写真URLを落として**候補シート**を作り、採用したものを記事へ差し込む。

**なぜ WebFetch を使わないか**: WebFetch は markdown へ変換する過程で、
**遅延読み込みの画像を `data:image/svg+xml` のプレースホルダーのまま返す**（2026-09-20 実測）。
生HTML を取って `src`/`data-src`/`srcset`/`og:image`/JSON-LD を全部見る `photo_urls_scan.py` を使う。

**Google Maps Platform は使わない**（2026-09-16 ユーザー指示「Google cloudは有料版入らない」）。
`places_fetch.py`・`place_photos_fetch.py` は `MAPS_KEY` を要求するので、この経路では触らない。

**採否は人が目で決める**（規約 §3-3「取得した写真は必ず1枚ずつ目視確認してから採用する」）。
このスクリプトは**候補を並べるところまで**で、選ばない。

使い方:
  python3 notion/photos_install.py fetch  <urls.json> <outdir>   # 落として候補シートを作る
  python3 notion/photos_install.py adopt  <picks.json>           # 採用したものを記事へ差し込む

  urls.json  = [{"path": "europe/belgium/leuven.html", "sid": "notre-dame",
                 "name": "Notre Dame", "urls": ["https://…jpg", …]}, …]
  picks.json = [{"path": …, "sid": …, "url": "採用した1本", "src_page": "出典ページ"}, …]
"""
import io, json, os, re, sys, urllib.request
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125 Safari/537.36"}
MIN_PX = 480            # これ未満はカードの hero（68mm）に耐えない


def get(u, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout).read()


def fetch(urls_json, outdir):
    rows = json.load(io.open(urls_json, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    got = []
    for r in rows:
        d = os.path.join(outdir, r["sid"])
        os.makedirs(d, exist_ok=True)
        n = 0
        for k, u in enumerate(r.get("urls", [])[:10], 1):
            p = os.path.join(d, "%02d.jpg" % k)
            try:
                b = get(u)
                open(p, "wb").write(b)
                im = Image.open(p)
                # **小さすぎる画像は捨てる。** サムネイルを掴むと紙面で潰れる。
                if min(im.size) < MIN_PX:
                    os.remove(p)
                    continue
                n += 1
            except Exception:
                if os.path.exists(p):
                    os.remove(p)
        got.append((r["sid"], n, len(r.get("urls", []))))
        sheet(d, r.get("name", r["sid"]))
    print("店 %d / 候補が1枚以上 %d 店" % (len(got), sum(1 for g in got if g[1])))
    for sid, n, m in got:
        if n == 0:
            print("   候補0: %s（URL %d 本とも落とせないか小さすぎ）" % (sid, m))


def sheet(d, title, cols=3, w=420):
    fs = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
    if not fs:
        return
    ims = []
    for f in fs:
        try:
            im = Image.open(os.path.join(d, f)).convert("RGB")
            ims.append((f, im.resize((w, int(im.height * w / im.width)))))
        except Exception:
            pass
    if not ims:
        return
    rows = (len(ims) + cols - 1) // cols
    hs = [max(im.height for _, im in ims[r * cols:(r + 1) * cols] or [(None, Image.new("RGB", (1, 1)))])
          for r in range(rows)]
    out = Image.new("RGB", (w * cols, sum(hs)), "white")
    for i, (f, im) in enumerate(ims):
        r, c = divmod(i, cols)
        out.paste(im, (c * w, sum(hs[:r])))
    out.save(os.path.join(d, "_sheet.png"))


def adopt(picks_json):
    """採用した1本を `img/<市>/<sid>.jpg` へ置き、記事の店カードへ hero を差し込む。"""
    picks = json.load(io.open(picks_json, encoding="utf-8"))
    by_path = {}
    for p in picks:
        by_path.setdefault(p["path"], []).append(p)
    for path, ps in by_path.items():
        d = os.path.dirname(path)
        city = os.path.basename(path)[:-5]
        s = io.open(path, encoding="utf-8").read()
        n = 0
        for p in ps:
            sid = p["sid"]
            dst = os.path.join(d, "img", city, sid + ".jpg")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if p.get("file"):
                open(dst, "wb").write(open(p["file"], "rb").read())
            else:
                open(dst, "wb").write(get(p["url"]))
            key = '<div class="card" id="c-%s">' % sid
            if key not in s:
                print("   カードが無い: %s" % sid)
                continue
            i = s.index(key) + len(key)
            if re.search(r'<img[^>]*class="hero"', s[i:i + 700]):
                continue                      # 既に写真がある＝触らない（冪等）
            img = ('\n  <img class="hero" src="img/%s/%s.jpg" alt="%s 料理・店内写真">'
                   % (city, sid, sid))
            s = s[:i] + img + s[i:]
            n += 1
        io.open(path, "w", encoding="utf-8").write(s)
        print("%-40s 写真を入れた %d 店" % (path, n))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "fetch":
        fetch(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "adopt":
        adopt(sys.argv[2])
    else:
        sys.exit(__doc__)
