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
DB_ID = os.environ.get("NOTION_DB_ID", "47b9d644-0415-472c-9bcb-8be35daf5cb0").strip()
LIMIT_IMAGES = int(os.environ.get("LIMIT_IMAGES", "0") or 0)
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"
API = "https://api.notion.com/v1"
VER = os.environ.get("NOTION_VERSION", "2022-06-28")

# 既存の店舗DBビューを持つページは全置換できない（子DBを消してしまう）
APPEND_ONLY = {"europe_belgium_leuven"}

S = requests.Session()
S.headers.update({"Authorization": "Bearer " + TOKEN, "Notion-Version": VER})


# ---------------------------------------------------------------- 低レベル

def api(method, path, **kw):
    for attempt in range(6):
        r = S.request(method, API + path, timeout=120, **kw)
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


def upload_image(path):
    """Notion にファイルを上げて file_upload_id を返す。"""
    fn = os.path.basename(path)
    ctype = mimetypes.guess_type(fn)[0] or "image/jpeg"
    up = api("POST", "/file_uploads", json={"filename": fn, "content_type": ctype})
    fid = up["id"]
    with open(path, "rb") as fh:
        r = S.post(up["upload_url"], files={"file": (fn, fh, ctype)}, timeout=300)
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

def clear_page(page_id):
    """ページ本文を空にする（子DBがあるページには使わないこと）。"""
    while True:
        res = api("GET", "/blocks/%s/children?page_size=100" % page_id)
        kids = res.get("results", [])
        if not kids:
            return
        for b in kids:
            api("DELETE", "/blocks/" + b["id"])
        if not res.get("has_more"):
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
    titles = {}
    for p in parts:
        base = p.split(".part")[0]
        titles.setdefault(base, base)

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
            pid = create_page(titles.get(base, base), None)
            pages[base] = pid
            print("   + created page", pid)

        first = part.endswith(".part01.md")
        if first and base not in APPEND_ONLY:
            clear_page(pid)
        append_blocks(pid, blocks)
        written.add(part)
        written_now.append(part)
        state["written_parts"] = sorted(written)
        state["pages"] = pages
        save_json(STATE, state)
        print("   -> wrote %d blocks to %s" % (len(blocks), pid))

        # そのガイドの全 part を書き終えたら死んだリンクを消す
        guide_parts = [q for q in parts if q.split(".part")[0] == base]
        if all(q in written for q in guide_parts):
            clear_dead_links(pid)

    state["uploads"] = uploads
    state["written_parts"] = sorted(written)
    state["pages"] = pages
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
