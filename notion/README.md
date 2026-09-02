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
  - `only` にガイド名の一部（例 `japan_osaka_suita`）を入れると、そのガイドだけを処理する

## 仕様メモ

- 画像は Notion の File Upload API で上げ、`image` ブロックとして各店カードの直下に置く
- **目次**: パート1の冒頭に「📑 目次（タップで開く）」のトグルを置き、その中に Notion 標準の
  目次ブロック（`table_of_contents`）を入れる。ジャンル見出しと店名見出しを Notion が自動で拾うので、
  店が増減しても手直しは要らない
- **店舗マップ**: HTML の `<div class="mapsec">` から全域マップ・拡大マップを取り込み、目次の直後に置く。
  Notion は画像内リンクを再現できないので、HTML版の「ピンをタップ」の文言は落として注記に差し替える。
  地図画像が無い欧州8冊（ブリュッセル・リエージュ・ルーベン・ヘント・パリ・アムステルダム・
  ケルン・フランクフルト）では地図の節そのものを出さない
- 地図画像は元が最大5.25MBあるので、**長辺1600px・256色PNG に落としてから**上げる
  （Notion の1ファイル上限は無料プランで5MB。地図は線と文字が主体なので JPEG より 256色PNG が読みやすい。
  4MBを超えたときだけ JPEG 品質85 に落とす）。リポジトリ内の元PNGは変更しない
- **本文が変わったガイドは自動で書き直す**。パートごとの SHA-1 を `upload_state.json` の `part_hash` に持ち、
  1つでも変わっていればそのガイドの**全パート**を書き直す（パート1がページを消してから書く作りなので、
  途中のパートだけの差し替えはできない）。写真は `uploads` に file_upload_id が残るので上げ直さない
- `dry_run` のときは状態ファイル（`upload_state.json`・`map.tsv`）を書き換えない
- パート1は既存本文を消してから書き、パート2以降は追記する
- **ルーベン（`europe_belgium_leuven`）だけは全置換しない**。既存の店舗DBビューがあり、
  消すと子データベースごと失われるため追記のみ（`APPEND_ONLY`）
- ガイドの全パートを書き終えたら、そのページの `PDF原本` / `HTML原本` を空にする
  （ai-memory 側の旧パスを指していて 404 のため）
- Notion ページが未作成のガイドは自動で作る（タイトル・種別・トピック・ステータス・収録店数）
- レート制限（429）と 5xx はリトライする
