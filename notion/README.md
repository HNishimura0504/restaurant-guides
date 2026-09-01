# 美食ガイド → Notion 本文化（写真つき）

美食ガイドの HTML を **Notion 成果物DB の記事本文**として書き込む仕組み。
写真も各店カードに載せる。GitHub Actions（クラウド）で動くので、手元のPCは関係ない。

## 中身

| パス | 役割 |
|---|---|
| `notion/build_md.py` | リポジトリ内の `<region>/<country>/<city>.html` を走査して Notion 用 Markdown へ変換 |
| `notion/guides_md/` | 変換結果。1ガイドを複数パートに分割（1回の書き込みを19,000字以下に抑えるため） |
| `notion/img_manifest.json` | 画像の対応表（パート → 画像のリポジトリ相対パス） |
| `notion/map.tsv` | ガイド → Notion ページID |
| `notion/state/upload_state.json` | 進捗（アップロード済み画像・書き込み済みパート・ページID） |
| `notion/sync.py` | Notion API を直接叩いて画像アップロード＋本文書き込み |
| `.github/workflows/notion-sync.yml` | 毎晩02:43 JST に実行。手動実行も可 |

## セットアップ（最初の1回だけ）

1. <https://www.notion.so/my-integrations> で内部インテグレーションを作り、トークン（`ntn_...`）を控える
2. Notion で **成果物DB** を開き、右上「…」→「接続」から 1 のインテグレーションを追加する
   （これをしないと API から見えない）
3. このリポジトリの Settings → Secrets and variables → Actions で
   - Secret に `NOTION_TOKEN` = 1 のトークン
   - （任意）Variable に `NOTION_DB_ID` = 成果物DBのID。未設定なら既定値を使う

## 動かし方

- 放っておけば毎晩 02:43 JST に走り、終わっていなければ続きを進める
- 手動で全部やるなら Actions タブ →「Notion 本文化（写真つき）」→ Run workflow
  - `limit_images` = 0 なら最後までやる。少しずつ試すなら 50 など
  - `dry_run` = 1 なら Notion に書き込まず、ブロック生成だけ検証する

## 仕様メモ

- 画像は Notion の File Upload API で上げ、`image` ブロックとして各店カードの直下に置く
- パート1は既存本文を消してから書き、パート2以降は追記する
- **ルーベン（`europe_belgium_leuven`）だけは全置換しない**。既存の店舗DBビューがあり、
  消すと子データベースごと失われるため追記のみ（`APPEND_ONLY`）
- ガイドの全パートを書き終えたら、そのページの `PDF原本` / `HTML原本` を空にする
  （ai-memory 側の旧パスを指していて 404 のため）
- Notion ページが未作成のガイドは自動で作る（タイトル・種別・トピック・ステータス・収録店数）
- レート制限（429）と 5xx はリトライする
