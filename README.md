# レストランガイド 総合インデックス

> **このリポジトリ（`HNishimura0504/restaurant-guides`）＝ ガイド成果物の単一の正。**
> 1冊分の HTML・写真・PDF が**同じフォルダに揃っている**（HTML の `src="img/<市>/…"` がそのまま解決する）。
> 2026-08-21 に `ai-memory` から分離した（メモリ本体を軽く保つため）。
>
> | 置き場 | 中身 |
> |---|---|
> | **本リポジトリ** | ガイド一式（HTML・`*_places.json`・`img/`・完成PDF）。**編集・再生成はここで行う** |
> | `ai-memory` | 作り方の規約 `topics/restaurant-guides/notes/playbook.md`、進捗ログ `log/`、写真取得スクリプト `assets/`、本インデックスへの参照 |
> | `ai-memory-archive` | 2026-08-21 以前の全履歴（旧パス `topics/restaurant-guides/output/…`）。**過去版を追うときだけ見る** |
>
> 本リポジトリのコミット履歴は 2026-08-21 の1コミットから始まる（それ以前は `ai-memory-archive` 側にある）。

レストランガイド（フル形式: 実写写真付きHTML + スマホ判型PDF）の保管場所。

**構成は「国 → 行政区分」の2段で統一**する。
- 日本: `japan/<県ローマ字>/` に `<市ローマ字>.html`・`<市和名>美食ガイド_スマホ版.pdf`・`img/<市ローマ字>/`
- 欧州: `europe/<国ローマ字>/` に `<都市ローマ字>.html`・`<都市和名>美食ガイド_スマホ版.pdf`・`img/<都市ローマ字>/`
- アジア(日本以外): `asia/<国ローマ字>/` に同様

同じ県・国のフォルダが既にあれば**新規フォルダを作らず既存へ追加**し、本インデックスへ1行足す。

> PDFはGitHubのプレビューではタップジャンプが効かない。**ファイルを開いて「Download raw file」でダウンロードし、PDFビューアで開く**と目次・マップのピンからジャンプできる。

## 日本

| 都道府県 | 都市 | 店数 | 場所 |
|---|---|---:|---|
| 北海道 | 札幌市 | 71 | [japan/hokkaido/](japan/hokkaido/) |
| 北海道 | 旭川市 | 44 | [japan/hokkaido/](japan/hokkaido/) |
| 青森県 | 青森市 | 46 | [japan/aomori/](japan/aomori/) |
| 青森県 | 八戸市 | 47 | [japan/aomori/](japan/aomori/) |
| 岩手県 | 盛岡市 | 50 | [japan/iwate/](japan/iwate/) |
| 岩手県 | 一関市 | 40 | [japan/iwate/](japan/iwate/) |
| 宮城県 | 仙台市 | 74 | [japan/miyagi/](japan/miyagi/) |
| 宮城県 | 石巻市 | 53 | [japan/miyagi/](japan/miyagi/) |
| 秋田県 | 秋田市 | 56 | [japan/akita/](japan/akita/) |
| 秋田県 | 横手市 | 47 | [japan/akita/](japan/akita/) |
| 山形県 | 山形市 | 57 | [japan/yamagata/](japan/yamagata/) |
| 山形県 | 鶴岡市 | 50 | [japan/yamagata/](japan/yamagata/) |
| 福島県 | 福島市 | 57 | [japan/fukushima/](japan/fukushima/) |
| 福島県 | 郡山市 | 53 | [japan/fukushima/](japan/fukushima/) |
| 茨城県 | 水戸市 | 54 | [japan/ibaraki/](japan/ibaraki/) |
| 茨城県 | つくば市 | 53 | [japan/ibaraki/](japan/ibaraki/) |
| 栃木県 | 宇都宮市 | 79 | [japan/tochigi/](japan/tochigi/) |
| 栃木県 | 小山市 | 47 | [japan/tochigi/](japan/tochigi/) |
| 群馬県 | 前橋市 | 49 | [japan/gunma/](japan/gunma/) |
| 群馬県 | 高崎市 | 48 | [japan/gunma/](japan/gunma/) |
| 埼玉県 | さいたま市 | 70 | [japan/saitama/](japan/saitama/) |
| 埼玉県 | 川口市 | 62 | [japan/saitama/](japan/saitama/) |
| 千葉県 | 千葉市 | 69 | [japan/chiba/](japan/chiba/) |
| 千葉県 | 船橋市 | 64 | [japan/chiba/](japan/chiba/) |
| 東京都 | 東京23区 | 70 | [japan/tokyo/](japan/tokyo/) |
| 東京都 | 八王子市 | 67 | [japan/tokyo/](japan/tokyo/) |
| 神奈川県 | 横浜市 | 68 | [japan/kanagawa/](japan/kanagawa/) |
| 神奈川県 | 川崎市 | 71 | [japan/kanagawa/](japan/kanagawa/) |
| 新潟県 | 新潟市 | 67 | [japan/niigata/](japan/niigata/) |
| 新潟県 | 長岡市 | 48 | [japan/niigata/](japan/niigata/) |
| 富山県 | 富山市 | 55 | [japan/toyama/](japan/toyama/) |
| 富山県 | 高岡市 | 47 | [japan/toyama/](japan/toyama/) |
| 大阪府 | 大阪市 | 72 | [japan/osaka/](japan/osaka/) |
| 大阪府 | 吹田市 | 49 | [japan/osaka/](japan/osaka/) |
| 大阪府 | 藤井寺市 | 45 | [japan/osaka/](japan/osaka/) |
| 京都府 | 京都市 | 71 | [japan/kyoto/](japan/kyoto/) |

小計 36冊 / 2070店

## 欧州

| 国 | 都市 | 店数 | 場所 |
|---|---|---:|---|
| ベルギー | ブリュッセル | 36 | [europe/belgium/](europe/belgium/) |
| ベルギー | ヘント | 37 | [europe/belgium/](europe/belgium/) |
| ベルギー | ルーベン | 36 | [europe/belgium/](europe/belgium/) |
| ベルギー | リエージュ | 37 | [europe/belgium/](europe/belgium/) |
| オランダ | アムステルダム | 37 | [europe/netherlands/](europe/netherlands/) |
| ドイツ | ケルン | 37 | [europe/germany/](europe/germany/) |
| ドイツ | フランクフルト | 35 | [europe/germany/](europe/germany/) |
| フランス | パリ | 36 | [europe/france/](europe/france/) |

小計 8冊 / 291店

## アジア（日本以外）

| 国 | 都市 | 店数 | 場所 |
|---|---|---:|---|
| ネパール | カトマンズ | 63 | [asia/nepal/](asia/nepal/) |

小計 1冊 / 63店

**合計 45冊 / 2424店**（2026-08-25 時点）

## 進行中の発注

**47都道府県ガイド**（毎日01:06 JSTに1県2都市ずつ自動作成）。進捗・都市ペア・手順は [`log/prefecture_guide_progress.md`](../log/prefecture_guide_progress.md) が正本。
単発の指名依頼（欧州8都市・カトマンズなど）の実行ログは [`log/spot_order_guides.md`](../log/spot_order_guides.md)。
作成手法（写真ルール・パイプライン・店数基準）は [`notes/playbook.md`](../notes/playbook.md)。

## 補足

- `japan/kansai_markdown_simple_20260801.md` — 最初期のMarkdown簡易版（吹田・大阪・藤井寺・京都の62店）。フル形式版が上位互換なので参照用。
- `<都市>_places.json` は Google Places API から取得した place_id・写真リソース名の control ファイル（フランクフルトのみ未作成）。
- **来歴**: 欧州8都市は 2026-08-06 まで公開リポジトリ `HNishimura0504/test` のルート直下にあったものを、本リポジトリ（非公開）へ集約した。ルーベンの写真は `img/` 直下に散在していたため `img/leuven/` へ正規化し、HTML の参照も更新済み。
- **ルーベン差し替え（2026-08-17）**: 2026-08-06 の集約時に混入していた旧19店版（Street View 外観写真＝現行ルール違反）を、正規の36店版（test ブランチ `claude/restaurant-database-expansion-ihrmop`・料理/店内実写のみ）へ全面差し替え。写真36枚＋他7都市238枚の全数目視検証済み（違反はルーベン旧版のみ）。PDFは #90 の内部リンク後処理（明示的宛先化）適用済み。
- 旧 `pref_guides/` は `japan/` へ改称（2026-08-06）。旧 `kansai_guides/` は 2026-08-06 に県別へ統合済み。
- **神奈川・新潟の写真とPDFを追加（2026-08-24）**。2026-08-21 の分離時、この2県はHTMLと
  control ファイルだけが移り、`img/` と完成PDFが ai-memory 側のワークツリーに残っていた
  （ai-memory の `.gitignore` がバイナリを弾くため、どちらの git にも入っていなかった）。
  今回収容し、**全冊が「HTML・写真・PDF が同じフォルダに揃う」状態**になった。
