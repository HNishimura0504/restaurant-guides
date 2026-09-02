# -*- coding: utf-8 -*-
"""美食ガイドを Notion の成果物DBへ「写真つきの記事本文」として書き込む。

GitHub Actions から動かす前提。MCP を介さず Notion API を直接叩くので、
画像アップロードも本文書き込みも一気に片付く。

必要な環境変数:
  NOTION_TOKEN   Notion インテグレーションのトークン（ntn_... / secret_...）
  NOTION_DB_ID   成果物DBのID（既定あり）
  LIMIT_IMAGES   1回で処理する画像の上限（0＝無制限。既定0）
  DRY_RUN        1 なら Notion へ書き込まない

進捗は notion/state/upload_state.json に残す（ワークフローがコミットして戻す）。
"""
import io
import os
import re
import sys
import json
import time
import hashlib
import threading
import tempfile
import mimetypes

try:
    import requests
except ImportError:
    sys.exit("requests が要ります: pip install requests")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_DIR = os.path.join(ROOT, "notion", "guides_md")
MANIFEST = os.path.join(ROOT, "notion", "img_manifest.json")
MAP_TSV = os.path.join(ROOT, "notion", "map.tsv")
STATE = os.path.join(ROOT, "notion", "state", "upload_state.json")

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DB_ID = (os.environ.get("NOTION_DB_ID") or "47b9d644-0415-472c-9bcb-8be35daf5cb0").strip()
LIMIT_IMAGES = int(os.environ.get("LIMIT_IMAGES", "0") or 0)
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"
# 部分名を入れると、そのガイドだけを処理する（例: japan_osaka_suita）。空なら全部。
ONLY = os.environ.get("ONLY", "").strip()
API = "https://api.notion.com/v1"
VER = os.environ.get("NOTION_VERSION", "2022-06-28")

# clear_page が子DB/子ページを残すようになったので、全置換の除外は不要。
# 特別扱いが要るページが出たらここに base 名を足す。
APPEND_ONLY = set()

# スレッドごとに Session を分ける（requests.Session はスレッド安全ではない）。
_local = threading.local()


def S():
    s = getattr(_local, "sess", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"Authorization": "Bearer " + TOKEN, "Notion-Version": VER})
        _local.sess = s
    return s


# ---------------------------------------------------------------- 低レベル

def api(method, path, **kw):
    for attempt in range(6):
        r = S().request(method, API + path, timeout=120, **kw)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2)))
            continue
        if r.status_code >= 500:
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code >= 400:
            raise RuntimeError("%s %s -> %s %s" % (method, path, r.status_code, r.text[:400]))
        return r.json() if r.text else {}
    raise RuntimeError("retries exhausted: %s %s" % (method, path))


MAP_MAX_PX = 1600
MAP_SIZE_CAP = 4 * 1024 * 1024


def shrink_map(path):
    """店舗マップの画像を、長辺 MAP_MAX_PX・256色PNG に落としてから上げる。

    元の PNG は最大5.25MB（japan/tokyo/img/tokyo23/_map2.png）あり、
    Notion のファイルサイズ上限（無料プランは1ファイル5MB）に触れる。
    地図は線と文字が主体なので、JPEG より 256色PNG のほうが文字が潰れない
    （実測: 5.01MB → 256色PNG 1.82MB / JPEG品質85 1.02MB）。
    256色PNG が MAP_SIZE_CAP を超えたときだけ JPEG に落とす。

    戻り値は (実際に上げるパス, 後始末する一時ファイル or None)。
    リポジトリ内の元PNGには手を触れない。
    """
    if not os.path.basename(path).startswith("_map"):
        return path, None
    try:
        from PIL import Image
    except ImportError:
        print("   ! Pillow が無いので地図を縮小せずに上げる:", os.path.basename(path))
        return path, None
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if max(w, h) > MAP_MAX_PX:
        r = float(MAP_MAX_PX) / max(w, h)
        im = im.resize((max(1, int(w * r)), max(1, int(h * r))), Image.LANCZOS)

    stem = os.path.splitext(os.path.basename(path))[0]
    fd, tmp = tempfile.mkstemp(suffix="_" + stem + ".png")
    os.close(fd)
    im.convert("P", palette=Image.ADAPTIVE, colors=256).save(tmp, "PNG", optimize=True)
    if os.path.getsize(tmp) > MAP_SIZE_CAP:
        os.remove(tmp)
        fd, tmp = tempfile.mkstemp(suffix="_" + stem + ".jpg")
        os.close(fd)
        im.save(tmp, "JPEG", quality=85, optimize=True)
    return tmp, tmp


def upload_image(path):
    """Notion にファイルを上げて file_upload_id を返す。"""
    path, tmp = shrink_map(path)
    try:
        return _upload(path)
    finally:
        if tmp and os.path.isfile(tmp):
            os.remove(tmp)


def _upload(path):
    fn = os.path.basename(path)
    ctype = mimetypes.guess_type(fn)[0] or "image/jpeg"
    up = api("POST", "/file_uploads", json={"filename": fn, "content_type": ctype})
    fid = up["id"]
    with open(path, "rb") as fh:
        r = S().post(up["upload_url"], files={"file": (fn, fh, ctype)}, timeout=300)
    if r.status_code >= 400:
        raise RuntimeError("upload failed %s: %s %s" % (fn, r.status_code, r.text[:300]))
    if r.json().get("status") != "uploaded":
        raise RuntimeError("upload not confirmed: " + fn)
    return fid


# ---------------------------------------------------- Markdown -> Notion blocks

LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
CODE = re.compile(r"`([^`]+)`")


def rich(text):
    """**bold** / `code` / [text](url) だけを解釈して rich_text 配列にする。"""
    toks = []

    def push(s, ann=None, href=None):
        if not s:
            return
        while s:
            part, s = s[:2000], s[2000:]
            t = {"type": "text", "text": {"content": part}}
            if href:
                t["text"]["link"] = {"url": href}
            if ann:
                t["annotations"] = ann
            toks.append(t)

    pos = 0
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*(.+?)\*\*|`([^`]+)`")
    for m in pattern.finditer(text):
        push(text[pos:m.start()])
        if m.group(1) is not None:
            push(m.group(1), href=m.group(2))
        elif m.group(3) is not None:
            push(m.group(3), ann={"bold": True})
        else:
            push(m.group(4), ann={"code": True})
        pos = m.end()
    push(text[pos:])
    return toks[:100]


def md_to_blocks(md, uploads):
    """本文Markdown -> Notion ブロック配列。uploads は rel_path -> file_upload_id。"""
    blocks = []
    for raw in md.split("\n"):
        ln = raw.rstrip()
        if not ln.strip():
            continue
        if ln.strip() == "@@TOC@@":
            blocks.append({"object": "block", "type": "toggle", "toggle": {
                "rich_text": rich("📑 目次（タップで開く）"),
                "children": [{"object": "block", "type": "table_of_contents",
                              "table_of_contents": {"color": "gray"}}]}})
            continue
        m = re.match(r"^@@IMG:([^@]+)@@$", ln.strip())
        if m:
            fid = uploads.get(m.group(1))
            if fid:
                blocks.append({"object": "block", "type": "image",
                               "image": {"type": "file_upload", "file_upload": {"id": fid}}})
            continue
        if ln.strip() == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        elif ln.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                           "heading_3": {"rich_text": rich(ln[4:])}})
        elif ln.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": rich(ln[3:])}})
        elif ln.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                           "heading_1": {"rich_text": rich(ln[2:])}})
        elif ln.startswith("- "):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": rich(ln[2:])}})
        elif ln.startswith("> "):
            blocks.append({"object": "block", "type": "quote",
                           "quote": {"rich_text": rich(ln[2:])}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": rich(ln)}})
    return blocks


# ---------------------------------------------------------------- ページ操作

KEEP_TYPES = {"child_database", "child_page"}
DELETE_WORKERS = 8


def clear_page(page_id):
    """ページ本文を空にする。ただし子データベース／子ページは消さない
    （ルーベンのように店舗DBのビューが埋まっているページを壊さないため）。

    Notion には一括削除が無く1ブロック1リクエストなので、ここが同期全体の律速になる
    （1冊は600ブロック前後ある）。直列だと往復待ちで毎秒1件も出ないため、
    数本のスレッドに分けて Notion のレート上限（毎秒3件前後）まで詰める。
    429 は api() が Retry-After に従って待ち直す。
    """
    from concurrent.futures import ThreadPoolExecutor
    while True:
        res = api("GET", "/blocks/%s/children?page_size=100" % page_id)
        kids = res.get("results", [])
        targets = [b for b in kids if b.get("type") not in KEEP_TYPES]
        if not targets:
            return
        with ThreadPoolExecutor(max_workers=DELETE_WORKERS) as ex:
            list(ex.map(lambda b: api("DELETE", "/blocks/" + b["id"]), targets))
        if not res.get("has_more") and len(targets) == len(kids):
            return
        if not res.get("has_more") and not targets:
            return


def append_blocks(page_id, blocks):
    for i in range(0, len(blocks), 100):
        api("PATCH", "/blocks/%s/children" % page_id, json={"children": blocks[i:i + 100]})


def clear_dead_links(page_id):
    """404 になった GitHub リンクの列を空にする。"""
    try:
        api("PATCH", "/pages/" + page_id,
            json={"properties": {"PDF原本": {"url": None}, "HTML原本": {"url": None}}})
    except Exception as e:
        print("   ! link clear skipped:", str(e)[:120])


def create_page(title, stores):
    props = {
        "タイトル": {"title": [{"type": "text", "text": {"content": title}}]},
        "種別": {"select": {"name": "美食ガイド"}},
        "トピック": {"select": {"name": "restaurant-guides"}},
        "ステータス": {"select": {"name": "公開"}},
        "収録店数": {"number": stores},
    }
    try:
        res = api("POST", "/pages", json={"parent": {"database_id": DB_ID}, "properties": props})
    except Exception:
        res = api("POST", "/pages", json={"parent": {"database_id": DB_ID},
                                          "properties": {"タイトル": props["タイトル"]}})
    return res["id"]


# ---------------------------------------------------------------- 状態

def load_json(p, default):
    if os.path.isfile(p):
        return json.load(io.open(p, encoding="utf-8"))
    return default


def save_json(p, obj):
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    fh = io.open(p, "w", encoding="utf-8", newline="\n")
    fh.write(json.dumps(obj, ensure_ascii=False, indent=1))
    fh.close()


def load_map():
    m = {}
    if os.path.isfile(MAP_TSV):
        for ln in io.open(MAP_TSV, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if not ln or ln.startswith("#"):
                continue
            f = ln.split("\t")
            if len(f) >= 2 and f[1] and f[1] != "NEW":
                m[f[0]] = f[1]
    return m


def save_map(m, titles):
    fh = io.open(MAP_TSV, "w", encoding="utf-8", newline="\n")
    for base in sorted(m):
        fh.write("%s\t%s\t%s\n" % (base, m[base], titles.get(base, "")))
    fh.close()


# ---------------------------------------------------------------- 本体

def main():
    if not TOKEN and not DRY_RUN:
        sys.exit("NOTION_TOKEN が設定されていません")

    manifest = load_json(MANIFEST, [])
    state = load_json(STATE, {"uploads": {}, "written_parts": [], "pages": {}})
    uploads = state.setdefault("uploads", {})
    written = set(state.setdefault("written_parts", []))
    pages = state.setdefault("pages", {})
    pages.update(load_map())

    by_part = {}
    for r in manifest:
        by_part.setdefault(r["part"], []).append(r["path"])

    parts = sorted(f for f in os.listdir(MD_DIR) if f.endswith(".md"))
    if ONLY:
        parts = [p for p in parts if ONLY in p]
        print("ONLY=%s のため %d パートだけを対象にする" % (ONLY, len(parts)))
    titles = {}
    for p in parts:
        base = p.split(".part")[0]
        titles.setdefault(base, base)

    # 本文が変わったガイドは「そのガイドの全パート」を書き直す。
    # part01 がページを消してから書く作りなので、途中のパートだけ差し替えることはできない。
    # 初回はハッシュ台帳が空なので全ガイドが対象になる（＝目次・地図の反映が一度で行き渡る）。
    hashes = state.setdefault("part_hash", {})
    cur = {}
    for p in parts:
        h = hashlib.sha1(io.open(os.path.join(MD_DIR, p), encoding="utf-8").read().encode("utf-8"))
        cur[p] = h.hexdigest()

    by_base = {}
    for p in parts:
        by_base.setdefault(p.split(".part")[0], []).append(p)

    dirty = set()
    for base, ps in by_base.items():
        known = sorted(q for q in hashes if q.split(".part")[0] == base)
        if known != sorted(ps) or any(hashes.get(q) != cur[q] for q in ps):
            dirty.add(base)

    if not ONLY:
        for q in list(hashes):
            if q not in cur:
                del hashes[q]
        written = set(q for q in written if q in cur)
    written = set(q for q in written if q.split(".part")[0] not in dirty)
    if dirty:
        print("本文が変わった（または未記録の）ガイド %d 冊を書き直す" % len(dirty))

    uploaded_now = 0
    written_now = []
    budget_hit = False

    for part in parts:
        if part in written:
            continue
        base = part.split(".part")[0]
        needed = by_part.get(part, [])
        todo = [x for x in needed if x not in uploads]

        if LIMIT_IMAGES and uploaded_now + len(todo) > LIMIT_IMAGES:
            budget_hit = True
            break

        print("== %s  (images %d)" % (part, len(todo)))
        for rel in todo:
            full = os.path.join(ROOT, rel)
            if not os.path.isfile(full):
                print("   ! missing image", rel)
                continue
            if DRY_RUN:
                uploads[rel] = "DRYRUN"
            else:
                uploads[rel] = upload_image(full)
            uploaded_now += 1
            if uploaded_now % 25 == 0:
                print("   .. uploaded %d" % uploaded_now)
                if not DRY_RUN:
                    save_json(STATE, state)

        md = io.open(os.path.join(MD_DIR, part), encoding="utf-8").read()
        blocks = md_to_blocks(md, uploads)

        if DRY_RUN:
            print("   [dry] %d blocks" % len(blocks))
            written.add(part)
            written_now.append(part)
            continue

        pid = pages.get(base)
        if not pid:
            try:
                pid = create_page(titles.get(base, base), None)
            except Exception as e:
                print("   ! ページ作成に失敗したのでこのガイドは飛ばす:", str(e)[:200])
                continue
            pages[base] = pid
            state["pages"] = pages
            save_json(STATE, state)
            print("   + created page", pid)

        first = part.endswith(".part01.md")
        if first and base not in APPEND_ONLY:
            clear_page(pid)
        append_blocks(pid, blocks)
        written.add(part)
        written_now.append(part)
        hashes[part] = cur[part]
        state["written_parts"] = sorted(written)
        state["part_hash"] = hashes
        state["pages"] = pages
        save_json(STATE, state)
        print("   -> wrote %d blocks to %s" % (len(blocks), pid))

        # そのガイドの全 part を書き終えたら死んだリンクを消す
        guide_parts = [q for q in parts if q.split(".part")[0] == base]
        if all(q in written for q in guide_parts):
            clear_dead_links(pid)

    state["uploads"] = uploads
    state["written_parts"] = sorted(written)
    state["part_hash"] = hashes
    state["pages"] = pages
    if DRY_RUN:
        print("[dry] 状態ファイルは更新しない")
    else:
        save_json(STATE, state)
        save_map(pages, titles)

    total_imgs = len(manifest)
    print("---")
    print("images uploaded this run : %d" % uploaded_now)
    print("images total             : %d / %d" % (len(uploads), total_imgs))
    print("parts written this run   : %d" % len(written_now))
    print("parts total              : %d / %d" % (len(written), len(parts)))
    if budget_hit:
        print("LIMIT_IMAGES に達したので今回はここまで（次回続きから）")


if __name__ == "__main__":
    main()
