# 乳児連れ情報 深掘り調査ログ — フュッセン／ホーエンシュヴァンガウ／シュヴァンガウ 35 店

- 調査日: 2026-09-26（調査専用セッション `claude/baby-fuessen-20260926`）
- 対象: `europe/germany/control/research_fuessen.json` の `stores` 35 店
- 成果: `europe/germany/control/baby_fuessen.json`（店ごとの判定・根拠・出典 URL）

## 総括

| 区分 | 店数 |
|---|---|
| found（三項目のいずれかを出典付きで確定） | 29 |
| none（4 回以上検索＋公式閲覧でも何も出ず → ガイドでは「情報なし」） | 6 |
| partial（4 回未満で打ち切り → 「未確認」のまま） | 0 |
| **WebSearch 使用回数** | **200 回（セッション上限を使い切り）** |

項目別: ハイチェア「あり」24 店 ／ ベビーカー「可」21 店・「不可」1 店 ／ おむつ替え台「あり」1 店（Schlossbrauhaus のみ） ／ 子どもメニュー「あり」12 店。

## 使った情報源と読めた／読めなかった経路

| 情報源 | 結果 |
|---|---|
| 各店公式サイト | WebFetch で 33 店分を閲覧。乳児設備を明記していたのは Gasthof Krone（Hochstühle・Kindergeschirr・Ausmalsachen）、Restaurant Ludwigs（Kindergerichte）、Café Kainz（Kinderkarte）のみ。hotel-helmer.de は 503／接続不可、hotelruebezahl.de 独語ページはタイムアウト（英語ページで代替） |
| **Trip.com 店舗ページ**（設備欄 Amenities / Features & Vibe） | WebFetch では取れないが `curl -A Mozilla… -e google.com` で us./www./uk./au.trip.com から取得可（一部ロケールは 7.6 KB のブロックページ→他ロケールで再試行）。フュッセン（fussen-1040）・ホーエンシュヴァンガウ（46205）・シュヴァンガウ（25595）の一覧から店舗 ID を抽出し 27 店分を取得、住所一致を確認。**ハイチェア「High chairs」表示 20 店、「Accessibility」表示 19 店**。本調査の主力出典 |
| Allgäu FamilyGuide | 35 店中 Schlossbrauhaus のみ掲載（Wickelkommode・Hochstühle・Kinderspeisekarte 明記）。Rundweg Schwansee／Hopfensee の頁でベビーカー可を確認 |
| Reisen für Alle／erlebe.bayern／schwangau.de barrierefreiheit | Schlossbrauhaus の認証レポート（stufenlos・Tür 80 cm・6 cm Schwelle）。他店の認証なし。Hotel Hirsch は公式に「teilweise barrierefrei」認証を記載 |
| hohenschwangau.de（公式） | Kainz の Kinderkarte、城内ベビーカー不可・Informationszentrum に預け、**Schloss-Bräustüberl 横の有料 WC に乳児用おむつ替え台**（EUR 1、EU キー） |
| Wanderlog（店ページ・家族向けリスト） | 20 店超のページを閲覧。口コミ本文に乳児語が出たのは Schwanen（baby）、Seaside（pram accessible）、La Perla（daughter）のみ |
| speisekarte.de／swipein／HolidayCheck／golocal／11880／outdooractive／gastroguide | 閲覧可。設備欄は「Familienfreundliches Restaurant」「Terrasse」程度で、ハイチェアの明記なし |
| speisekarte.menu／menuweb／menu-world 系 | 検索スニペットに「Hochstühle」が出るが、ページ本体は JS 描画（約 5.6 KB）で読めず → Hechten・Frühlingsgarten・Weinbauer・Kurcafe はこのスニペットのみが根拠（note に明記） |
| TripAdvisor／Yelp／RestaurantGuru／TheFork | curl・WebFetch とも 403／503（実測）。検索スニペットの文言のみ使用（Krone のベビーカー拒否口コミ、Gebirgsjäger の遊び場等） |
| wanderboat.ai／mindtrip.ai／goyellow | 403／本文なし／410 |
| ammersee-lech-barrierefrei.de（Markthalle の項目） | 0 バイト応答で取得不可 |
| Google Maps Platform | 不使用（指示どおり） |

## 店ごとの検索回数と判定

| id | status | 検索 | ベビーカー | ハイチェア | おむつ替え | 子どもメニュー |
|---|---|---|---|---|---|---|
| gasthaus-zum-schwanen | found | 7 | 可 | あり | 情報なし | 情報なし |
| zum-hechten | found | 11 | 情報なし | あり | 情報なし | 情報なし |
| hotel-hirsch | found | 6 | 可 | あり | 情報なし | 情報なし |
| fruehlingsgarten | found | 4 | 情報なし | あり | 情報なし | 情報なし |
| mauchers | found | 4 | 可 | あり | 情報なし | 情報なし |
| ritterstuben | found | 8 | 可 | あり | 情報なし | 情報なし |
| gasthof-krone | found | 7 | 不可 | あり | 情報なし | 情報なし |
| madame-pluesch | found | 4 | 可 | あり | 情報なし | あり |
| haus-der-gebirgsjaeger | found | 5 | 可 | あり | 情報なし | あり |
| hotel-alatsee | none | 4 | 情報なし | 情報なし | 情報なし | あり |
| beim-ditsch | found | 5 | 情報なし | あり | 情報なし | 情報なし |
| restaurant-ludwigs | found | 4 | 可 | あり | 情報なし | あり |
| restaurant-mueller-hohenschwangau | found | 4 | 可 | あり | 情報なし | あり |
| schneiderhanser-hotel-helmer | found | 4 | 可 | あり | 情報なし | あり |
| wirtshaus-weinbauer | found | 7 | 情報なし | あり | 情報なし | 情報なし |
| louis-ii-ruebezahl | found | 4 | 可 | あり | 情報なし | あり |
| schlossrestaurant-neuschwanstein | found | 5 | 可 | 情報なし | 情報なし | あり |
| berggasthaus-bleckenau | found | 5 | 可 | あり | 情報なし | 情報なし |
| restaurant-cafe-kainz | found | 5 | 可 | あり | 情報なし | あり |
| alpenrose-am-see | none | 9 | 情報なし | 情報なし | 情報なし | 情報なし |
| konditorei-kurcafe | found | 6 | 情報なし | あり | 情報なし | 情報なし |
| cafe-freiday | none | 7 | 情報なし | 情報なし | 情報なし | 情報なし |
| caffe-lucca | found | 6 | 可 | 情報なし | 情報なし | 情報なし |
| bio-cafe-baumgarten | none | 5 | 情報なし | 情報なし | 情報なし | 情報なし |
| cafe-bistro-seaside | found | 6 | 可 | 情報なし | 情報なし | 情報なし |
| schlossbackstube-cafe-eis | found | 6 | 可 | 情報なし | 情報なし | 情報なし |
| schwansee-kiosk | found | 6 | 可 | 情報なし | 情報なし | 情報なし |
| schlossbrauhaus-schwangau | found | 4 | 可 | あり | あり | あり |
| markthalle-fuessen | none | 6 | 情報なし | 情報なし | 情報なし | 情報なし |
| la-perla-fuessen | found | 4 | 可 | あり | 情報なし | あり |
| stegos-fuessen | none | 6 | 情報なし | 情報なし | 情報なし | 情報なし |
| annapurna-fuessen | found | 5 | 情報なし | あり | 情報なし | 情報なし |
| wok-in-fuessen | found | 5 | 可 | あり | 情報なし | あり |
| il-pescatore-fuessen | found | 5 | 可 | あり | 情報なし | 情報なし |
| kyodai-fuessen | found | 5 | 情報なし | あり | 情報なし | 情報なし |

※ 複数店をまとめた検索（OR 検索）は各店に 1 回ずつ計上、地域一般の検索（Füssen Wickeltisch 等 10 回）は店に計上していないため、店別合計（194）＋地域（10）＞200 となる。

## 特記事項（ガイド本体に反映すべきもの）

- **Gasthof Krone**: 公式にハイチェア明記だが、TripAdvisor 口コミ（スニペット）に「ベビーカーは食堂に入れられず、外に置けば食事可」→ ベビーカー「不可」と判定（要確認）。
- **Restaurant Ritterstuben**: 30 年営業の Winter 夫妻が **2025-10-30 で閉店**（Füssen aktuell 2025-06-01）、2026 年初から新経営（グルテンフリー継続）。ガイドの店情報・営業時間の再確認が必要。
- **Schlossbrauhaus Schwangau**: 35 店で唯一おむつ替え台を確認（FamilyGuide „Wickelkommode vorhanden.“）。地下に遊戯室。
- **ホーエンシュヴァンガウ城下**: 店側におむつ替え台の記載はないが、Schloss-Bräustüberl 横の公衆 WC（EUR 1）に乳児用おむつ替え台（公式）。城内ベビーカー不可、Informationszentrum（城の中庭）に預ける。
- **Bio Café Baumgarten**: Yelp 表示は「車椅子非対応」、店内 3 卓の極小 → ベビーカー入店は現実的でない可能性。
- **Hotel Alatsee**: レストラン情報なしだが、Trip.com ホテル設備に Children's meals・Cribs。

## 全 200 検索の一覧（番号／店／クエリ／結果要旨）

| # | 店 | クエリ | 結果 |
|---|---|---|---|
| 1 | gasthaus-zum-schwanen | Gasthaus zum Schwanen Füssen Hochstuhl OR Kinderstuhl OR Wickeltisch OR Kinderwagen | nothing relevant (generic product pages) |
| 2 | gasthaus-zum-schwanen | Gasthaus zum Schwanen Füssen highchair OR "high chair" OR stroller OR "changing table" | nothing relevant |
| 3 | zum-hechten | Zum Hechten Füssen Restaurant Hochstuhl OR Kinderstuhl OR Wickeltisch OR Kinderwagen kinderfreundlich | official menu pages, tripadvisor (403), no baby info |
| 4 | zum-hechten | Zum Hechten Füssen restaurant highchair OR "high chair" OR stroller OR "changing table" family | nothing relevant |
| 5 | hotel-hirsch | Hotel Hirsch Füssen Restaurant Hochstuhl OR Kinderstuhl OR Wickeltisch OR Kinderwagen familienfreundlich | hotel babycot (Inklusivleistungen); no restaurant highchair info |
| 6 | hotel-hirsch | Hotel Hirsch Füssen restaurant highchair OR "high chair" OR stroller OR "changing table" baby | hotel baby bed only |
| 7 | gasthaus-zum-schwanen | wanderlog "Gasthaus zum Schwanen" Füssen | wanderlog list only; yelp/tripadvisor/restaurantguru links (unreadable) |
| 8 | zum-hechten | wanderlog "Zum Hechten" Füssen restaurant | wanderlog place page 224017; family-restaurants list 551886 |
| 9 | fruehlingsgarten | Frühlingsgarten Bad Faulenbach Füssen Restaurant Kinder Hochstuhl | summary claimed highchairs, source unverified (preiswert-uebernachten: Familienzimmer/Kinderermäßigung only; allgaeuerurlaubsportal: none; official restaurant page: none) |
| 10 | mauchers | Maucher's Hopfen am See Restaurant Kinder Hochstuhl Kinderwagen | review "Also to be recommended with children" (mindtrip/trip.com snippet); speisekarte.de none |
| 11 | ritterstuben | Ritterstuben Füssen Restaurant Kinder Hochstuhl Kinderwagen | summary claimed highchairs; holidaycheck & swipein pages: none |
| 12 | gasthof-krone | Gasthof Krone Füssen Kinder Hochstuhl Wickeltisch | official site: "Die kleinsten unter uns heißen wir mit Kindergeschirr, Hochstühlen und Ausmalsachen willkommen." (VERIFIED) |
| 13 | madame-pluesch | Madame Plüsch Füssen Kinder Hochstuhl Kinderwagen Wickeltisch | speisekarte.de "Familienfreundliches Restaurant"; swipein: Terrasse only; highchair claim unverified |
| 14 | haus-der-gebirgsjaeger | Haus der Gebirgsjäger Füssen Restaurant Kinder Hochstuhl Kinderwagen | speisekarte.de "Familienfreundliches Restaurant"; official gastronomie page: Biergarten only; playground/highchair claims unverified |
| 15 | hotel-alatsee | Hotel Alatsee Füssen Restaurant Kinder Hochstuhl Kinderwagen | nothing; official restaurant page none |
| 16 | beim-ditsch | Lila Haus OR "Beim Ditsch" Füssen Kinder Hochstuhl Kinderwagen | nothing; official about page none |
| 17 | restaurant-ludwigs | Hotel Ludwigs Füssen Restaurant Kinder Hochstuhl Wickeltisch Kinderwagen | official gastronomie: Kindergerichte "An unsere kleinen Gäste haben wir natürlich auch gedacht"; hotels.com: cribs & baby gates (hotel) |
| 18 | restaurant-mueller-hohenschwangau | Hotel Müller Hohenschwangau Restaurant Kinder Hochstuhl Wickeltisch Kinderwagen | expedia: kids' meals; official restaurant page none |
| 19 | schneiderhanser-hotel-helmer | Hotel Helmer Schwangau Schneiderhanser Restaurant Kinder Hochstuhl Wickeltisch | children's menu (official culinary page snippet); official page 503 on fetch |
| 20 | wirtshaus-weinbauer | Wirtshaus zum Weinbauer Schwangau Kinder Hochstuhl Kinderwagen | nothing; gastroguide, wanderlog place 2734712; official page none |
| 21 | louis-ii-ruebezahl | Rübezahl Schwangau Restaurant "Louis II" Kinder Hochstuhl Wickeltisch | summary claimed Hochstühle; speisekarte.de: "Familienfreundliches Restaurant ... Terrasse" only; official page timeout |
| 22 | schlossrestaurant-neuschwanstein | Schlossrestaurant Neuschwanstein Kinderwagen OR Hochstuhl ... | castle (not restaurant): stroller parking & changing table at castle entrance (blogwithlove/neuschwanstein.de); official restaurant page none |
| 23 | berggasthaus-bleckenau | Berggasthaus Bleckenau Kinderwagen OR Hochstuhl OR Kinder Wanderung | hiking portals; "Wanderungen mit dem Kinderwagen" guides exist; nothing on Hochstuhl |
| 24 | restaurant-cafe-kainz | Café Kainz Hohenschwangau Kinder Hochstuhl Kinderwagen | hohenschwangau.de: families welcome, children's menu (to verify) |
| 25 | alpenrose-am-see | Alpenrose am See Hohenschwangau AMERON Kinder ... | nothing specific (terrace; kiosk) |
| 26 | konditorei-kurcafe | Kurcafé OR "Kurcafe" Füssen Schlosskrone Kinder Hochstuhl ... | summary claimed Hochstühle (source unverified, maybe schlosskrone.de/en/restaurants.html) |
| 27 | cafe-freiday | Café Freiday OR "Cafe FREIDAY" Füssen Kinder Hochstuhl Kinderwagen | nothing; familienausflug.info list (Kinderwagen geeignet places, not the café) |
| 28 | caffe-lucca | Caffè Lucca OR "Caffe Lucca" Füssen Ritterstraße Kinder ... | kid-friendly label (wanderlog/yelp?) unverified |
| 29 | bio-cafe-baumgarten | Café Baumgarten Füssen Magnusplatz Kinder Hochstuhl Kinderwagen | very small (3 tables inside, 4-5 outside) per review snippet; nothing on highchair |
| 30 | cafe-bistro-seaside | Seaside Hopfensee Café Bistro Kinder Hochstuhl Kinderwagen Wickeltisch | child-friendly with suitable dishes (hopfen-see.de?); wanderlog list: "Wheelchair/pram accessible" |
| 31 | schlossbackstube-cafe-eis | Schlossbackstube Schwangau Café Eis Kinder Hochstuhl Kinderwagen | outdooractive: circular route ideal with baby carriage; nothing on highchair |
| 32 | schwansee-kiosk | Schwansee Kiosk Schwangau Kinderwagen Familie Spielplatz | FamilyGuide rundweg-schwansee: route stroller-suitable; toilets at kiosk in season |
| 33 | schlossbrauhaus-schwangau | Schlossbrauhaus Schwangau Kinder Hochstuhl Wickeltisch Kinderwagen Spielecke | FamilyGuide page "Ein Paradies für Familien" (to fetch); play room basement, garden, minigolf; one review "missing a high chair" (snippet, unverified) |
| 34 | markthalle-fuessen | Markthalle Füssen Kinder Hochstuhl Kinderwagen Wickeltisch | nothing; holidaycheck page |
| 35 | la-perla-fuessen | La Perla Füssen Drehergasse Pizzeria Kinder Hochstuhl Kinderwagen | summary claimed highchairs (source unverified: swipein/wanderboat/evendo); wanderlog list review "took such genuine, sweet care of our daughter" |
| 36 | stegos-fuessen | Stego's OR "Stegos" Füssen griechisches Restaurant Kinder ... | nothing; wanderlog place 10799759; swipein |
| 37 | annapurna-fuessen | Annapurna Füssen Restaurant Kemptener Straße Kinder ... | summary claimed highchairs (source unverified); patio |
| 38 | wok-in-fuessen | Wok In Füssen Reichenstraße Restaurant Kinder ... | great for children (snippet, unverified) |
| 39 | il-pescatore-fuessen | Il Pescatore Füssen Franziskanergasse Kinder ... | summary claimed highchairs + wheelchair accessible + terrace (source unverified) |
| 40 | kyodai-fuessen | KYŌDAI OR "Kyodai" Füssen Luitpoldstraße Restaurant Kinder ... | summary claimed high chairs (source unverified) |
| 41 | (all) | all-familyguide.de Füssen Restaurant Café Wickelkommode Hochstühle | FamilyGuide has Schlossbrauhaus only among our 35 (others: Stiftsterrassen, Am Kamin, Terminal 23, Gifthütte) |
| 42 | (all) | all-familyguide.de Schwangau Hohenschwangau Gastronomie Wickelkommode Hochstühle | Schlossbrauhaus, Gifthütte, Helmerhof (not Hotel Helmer) only |
| 43 | hotel-hirsch | wanderlog "Hotel Hirsch" Füssen restaurant reviews | outdoor seating; no baby info |
| 44 | gasthof-krone | wanderlog "Gasthof Krone" Füssen | wanderlog 4319592 (no baby mentions); swipein; trip.com found later |
| 45 | madame-pluesch | wanderlog "Madame Plüsch" Füssen | wanderlog 960751 (none); wanderboat (403) |
| 46 | ritterstuben | wanderlog "Ritterstuben" Füssen | wanderlog 1378245 (none); restaurantguru 4.8/1695 (unreadable) |
| 47 | fruehlingsgarten | wanderlog "Frühlingsgarten" Füssen | wanderlog 2071101 (none); holidaycheck hotel page; 95 seats inside + 60 terrace |
| 48 | mauchers | wanderlog "Maucher's" Hopfen am See | trip.com 37690701 -> curl: "Kid-friendly ... Amenities: Accessibility Parking High chairs Outdoor seating" (VERIFIED via curl 2026-09-26) |
| 49 | schwanen/hechten/ritterstuben/krone | trip.com restaurant Füssen "Gasthaus zum Schwanen" OR ... | trip.com Krone 19120670 -> curl: "Kid-friendly ... Amenities: Accessibility Pet-friendly High chairs Outdoor seating"; wanderlog schwanen 6117994 |
| 50 | pluesch/hirsch/fruehlingsgarten/ludwigs | trip.com restaurant Füssen "Madame Plüsch" OR ... | only tripadvisor/restaurantguru links (unreadable) |
| 51 | schlossrestaurant/kainz/mueller/bleckenau | trip.com restaurant Hohenschwangau ... | wanderlog schwangau family list 552764; tripadvisor links |
| 52 | gasthaus-zum-schwanen | Gasthaus zum Schwanen Füssen mit Kindern OR Baby OR Kinderwagen Erfahrung Bewertung | gastroguide/holidaycheck/swipein: none; swipein "Terrasse" |
| 53 | zum-hechten | Zum Hechten Füssen Restaurant mit Kindern OR Baby OR Kinderwagen Bewertung | nothing specific ("children are welcome" hotel listing skyscanner) |
| 54 | hotel-hirsch | Hotel Hirsch Füssen Bierstüberl Restaurant mit Kindern OR Kinderwagen OR Hochstuhl Bewertung | nothing on restaurant |
| 55 | schlossrestaurant-neuschwanstein | Schlossrestaurant Neuschwanstein Bewertung Kinder Hochstuhl Terrasse Familie | snippet: "Kindermahlzeiten sind ebenfalls verfügbar" (booking.com?), 4 Gasträume 200 Gäste + Terrasse/Garten; holidaycheck pi: none |
| 56 | berggasthaus-bleckenau | Bleckenau Berggasthaus Bewertung Kinder Hochstuhl Spielplatz Familie Kinderwagen Bus | swipein: Terrasse; holidaycheck review: bus hourly from Touristeninfo; nothing on Hochstuhl |
| 57 | restaurant-cafe-kainz | Kainz Hohenschwangau Restaurant Bewertung Kinderwagen Hochstuhl Familie | snippet: wheelchair-accessible entrance & parking (source unverified); official: Kinderkarte; speisekarte.de none |
| 58 | (area) | Hohenschwangau Neuschwanstein Restaurant Essen mit Baby Kinderwagen Hochstuhl Wickeltisch Erfahrungsbericht Blog | blogwithlove: castle cloakroom for buggy + changing table at castle; nothing on restaurants |
| 59 | (area) | Füssen Altstadt Café Restaurant mit Baby Kinderwagen Wickeltisch Hochstuhl Erfahrung Blog Familie | only Krone (already); tripadvisor kinderfreundlich list (unreadable) |
| 60 | markthalle-fuessen | Markthalle Füssen Bewertung Kinder Hochstuhl Wickeltisch Kinderwagen barrierefrei | ammersee-lech-barrierefrei.de entry (curl returned 0 bytes); "barrier-free accessible" snippet |
| 61 | ritterstuben | [trip.com] Ritterstuben Füssen restaurant | trip.com Ritterstub'n 19120710; Füssen list fussen-1040 |
| 62 | madame-pluesch | [trip.com] Madame Plüsch Füssen restaurant | no own page; found Beim Ditsch 60324477, La Perla 19120669 |
| 63 | zum-hechten | [trip.com] Zum Hechten Füssen restaurant | trip.com zum-hechten 19120672 |
| 64 | gasthaus-zum-schwanen | [trip.com] Gasthaus zum Schwanen Füssen restaurant | no Füssen page found |
| 65 | hotel-hirsch | [trip.com] Hotel Hirsch Füssen restaurant | hotel pages only (beer garden) |
| 66 | fruehlingsgarten | [trip.com] Frühlingsgarten Füssen restaurant | hotel page only (Biergarten) |
| 67 | restaurant-ludwigs | [trip.com] Restaurant Ludwigs Füssen | hotel page only (120 seats, patio) |
| 68 | schlossrestaurant-neuschwanstein | [trip.com] Schlossrestaurant Neuschwanstein Hohenschwangau restaurant | trip.com Zur-Neven-Burg 23874194 (=Zur Neuen Burg), Bistro 60323039 |
| 69 | restaurant-cafe-kainz | [trip.com] Cafe Kainz Hohenschwangau restaurant | no own page; Hohenschwangau list 46205; snippet: restrooms in basement free with coffee |
| 70 | schlossbrauhaus-schwangau | [trip.com] Schlossbrauhaus Schwangau restaurant | trip.com 17807202 |
| 71 | haus-der-gebirgsjaeger | Haus der Gebirgsjäger Füssen Bewertung Kinder Spielplatz Hochstuhl Familie | fuessen.de POI snippet: "Kinderspielplatz direkt am Haus"; POI page fetch: no text |
| 72 | hotel-alatsee | Alatsee Hotel Restaurant Füssen Bewertung Kinder Familie Hochstuhl Terrasse | hotel: Familienhotel, kids free <3; nothing on Hochstuhl |
| 73 | beim-ditsch | Beim Ditsch Füssen Bewertung Kinder Familie Hochstuhl | speisekarte.de "Familienfreundliches Restaurant"/"Terrasse"; tripadvisor review snippet "kind to children" |
| 74 | restaurant-mueller-hohenschwangau | Hotel Müller Hohenschwangau Bewertung Kinder Familie Hochstuhl Babybett Kinderstuhl | kids' meals (expedia); cots on request; nothing on Hochstuhl |
| 75 | schneiderhanser-hotel-helmer | Hotel Helmer Schwangau Familie Kinder Hochstuhl Babybett Spielplatz Kinderkarte | Babybett (booking); play room/garden snippets belong to Helmerhof (different hotel) |
| 76 | wirtshaus-weinbauer | Weinbauer Schwangau Wirtshaus Bewertung Familie Kinder Hochstuhl Kinderkarte | snippet claimed high chairs (source unverified; speisekarte.de & swipein: none) |
| 77 | louis-ii-ruebezahl | Rübezahl Schwangau Hotel Familie Kinder Hochstuhl Babybett Kinderkarte Restaurant | familien-hotel-angebote.de: "Unser Restaurant punktet mit speziellen Kindergerichten - Kinderstühle im Restaurantbereich sind bei uns selbstverständlich." (VERIFIED fetch) |
| 78 | alpenrose-am-see | Alpenrose am See Bewertung Kinder Familie Kinderwagen Hochstuhl Terrasse Alpsee | holidaycheck pi: Terrasse only; Lermoos hotel noise |
| 79 | konditorei-kurcafe | Kurcafe Füssen Bewertung Kinder Familie Hochstuhl Kinderwagen | holidaycheck.ch review tag "mit Terrasse / Garten / kinderfreundlich"; snippet claims Hochstühle (unverified) |
| 80 | cafe-freiday | Freiday Café Füssen Bewertung Kinder Familie Hochstuhl Kinderwagen | nothing; wanderlog 10980029 none |
| 81 | caffe-lucca | Caffè Lucca Füssen Bewertung Kinder Familie Hochstuhl Frühstück | snippet: kinderfreundlich, rollstuhlgerecht (source unverified); speisekarte.de/11880: none |
| 82 | bio-cafe-baumgarten | Bio Café Baumgarten Füssen Bewertung Kinder Familie Hochstuhl | family reviews; very small interior; nothing on Hochstuhl |
| 83 | cafe-bistro-seaside | Seaside Hopfen am See Café Bewertung Kinder Familie Hochstuhl Kinderwagen Spielplatz | snippet "child-friendly with appropriate dishes" (source unverified); golocal none |
| 84 | schlossbackstube-cafe-eis | Schlossbackstube OR "Café Sauerwein" Schwangau Bewertung Kinder Familie Hochstuhl Kinderwagen | self-service, terrace+interior, parking; nothing on Hochstuhl |
| 85 | schwansee-kiosk | Schwansee Kiosk Schwangau Bewertung Kinder Familie Kinderwagen Toilette Wickeln | schwangau.de POI: open Apr-Oct 10-18 good weather; FamilyGuide: Kinderwagen möglich; toilets in season |
| 86 | la-perla-fuessen | La Perla Füssen Pizzeria Bewertung Kinder Familie Hochstuhl Kinderwagen | snippet: Kinderportionen, Hochstühle (unverified); holidaycheck/golocal/11880: none |
| 87 | stegos-fuessen | Stego's Taverna Füssen Bewertung Kinder Familie Hochstuhl Terrasse | outdoor seating pedestrian street + Innenhof (tripadvisor snippet); nothing on Kinder |
| 88 | annapurna-fuessen | Annapurna Füssen indisches Restaurant Bewertung Kinder Familie Hochstuhl | snippet Hochstühle (unverified); family reviews |
| 89 | wok-in-fuessen | Wok In Füssen Bewertung Kinder Familie Hochstuhl | speisekartenweb: menu section "für Kinder" (Pommes 3.50 / Pommes mit paniertem Hähnchen 6.50) VERIFIED |
| 90 | il-pescatore-fuessen | Il Pescatore Füssen Bewertung Kinder Familie Hochstuhl Terrasse | snippet: kinderfreundlich, Hochstühle, interior limited (unverified); speisekarte.de "Familienfreundliches Restaurant" |
| 91 | kyodai-fuessen | KYŌDAI Füssen sushi kids OR children OR "high chair" ... | Familien Essen Friday; yelp result is a different KYODAI (US) |
| 92 | kyodai-fuessen | Kyodai Füssen Bewertung Kinder Familie Hochstuhl Terrasse | family review snippet; familienfreundlich, Terrasse |
| 93 | haus-der-gebirgsjaeger | Haus der Gebirgsjäger Füssen restaurant kids OR children ... | tripadvisor snippet: indoor+outdoor playgrounds, highchairs, kids menu (unverified snippet) |
| 94 | hotel-alatsee | Alatsee hotel restaurant Füssen kids OR children ... | trip.com hotel: cribs, kids meals; games corner |
| 95 | beim-ditsch | Beim Ditsch Füssen kids OR children OR "high chair" ... | nothing (product noise) |
| 96 | schneiderhanser-hotel-helmer | Hotel Helmer Schwangau restaurant kids OR children ... | Helmerhof (other) highchairs; trip.com hotel Helmer: children's meals, playground, cribs |
| 97 | wirtshaus-weinbauer | Weinbauer Schwangau restaurant kids OR children ... | tripadvisor hotel review snippet: "staff bringing over a high chair for an infant during breakfast" (hotel breakfast) |
| 98 | alpenrose-am-see | Alpenrose am See Hohenschwangau kids OR children ... | trip.com: Kid-friendly; outdoor seating; nothing on high chairs |
| 99 | konditorei-kurcafe | Kurcafe OR "Kurcafé" Füssen cafe kids OR children ... | nothing (product noise) |
| 100 | cafe-freiday | Cafe Freiday OR "Café FREIDAY" Füssen kids OR children ... | nothing (product noise) |
| 101 | caffe-lucca | Caffè Lucca Füssen kids OR children ... | nothing specific |
| 102 | bio-cafe-baumgarten | Baumgarten Füssen cafe crepes kids OR children ... | yelp "Good for kids" (snippet); small indoor |
| 103 | mauchers | Maucher's Hopfen am See Wickeltisch OR Kinderwagen OR barrierefrei ... | snippets: "provided a high chair when requested", barrier-free (unverified); official: Terrasse 40 / Gastraum 45 Sitzplätze |
| 104 | louis-ii-ruebezahl | Louis II Rübezahl Schwangau Wickeltisch OR Kinderwagen OR barrierefrei ... | nothing (Michelin hotel listing) |
| 105 | cafe-bistro-seaside | Seaside Hopfensee Uferstraße barrierefrei OR Rollstuhl OR Kinderwagen OR Hochstuhl | snippet: wheelchair accessible + parking (restaurantguru/yelp, unverified) |
| 106 | schlossbackstube-cafe-eis | Schlossbackstube Schwangau Füssener Straße 15 Café Bewertung Familie Kinder Hochstuhl ... | nothing on Hochstuhl; parking next to building |
| 107 | schwansee-kiosk | Schwansee Kiosk Schwangau Baby Kinderwagen Rundweg Wickeln Erfahrung Blog | familienurlaub-info: Rundweg family & stroller friendly; 300 m from parking past kiosk |
| 108 | markthalle-fuessen | Markthalle Füssen Bewertung Familie Kinder Hochstuhl OR Kinderwagen ... | nothing |
| 109 | la-perla-fuessen | La Perla Füssen Wickeltisch OR Kinderwagen OR barrierefrei ... | nothing (product noise) |
| 110 | stegos-fuessen | Stego's OR "Stegos" Füssen Greek restaurant kids OR children ... | nothing |
| 111 | annapurna-fuessen | Annapurna Füssen Indian restaurant kids OR children ... | review: party with 3 kids; parking in front; nothing on high chairs |
| 112 | wok-in-fuessen | Wok In Füssen Asian restaurant kids OR children ... | great for children review snippets |
| 113 | il-pescatore-fuessen | Il Pescatore Füssen Italian restaurant kids OR children ... | here with a large family with small children (review snippet); small, reserve |
| 114 | schlossbrauhaus-schwangau | Schlossbrauhaus Schwangau Kinderwagen OR barrierefrei OR Wickeltisch ... | erlebe.bayern "Reisen für Alle": stufenlos/Aufzug, Türen ≥80 cm, 7 Behindertenparkplätze, WC (VERIFIED fetch); Biergarten 6 cm Schwelle |
| 115 | (area) | erlebe.bayern "Urlaub für Alle" Schwangau OR Füssen ... zertifiziert | only Tourist Info Schwangau + Schlossbrauhaus |
| 116 | (area) | Reisen für Alle zertifiziert Restaurant Café Füssen ... Wickeltisch | nothing more |
| 117 | zum-hechten | Zum Hechten Füssen Hotel Familienzimmer Babybett Kinder Restaurant Hochstuhl | hotel: family rooms, cots €8 (<2y); nothing on restaurant Hochstuhl |
| 118 | wirtshaus-weinbauer | Hotel Weinbauer Schwangau Kinder Babybett Hochstuhl Frühstück Familie | very family friendly hotel; nothing specific |
| 119 | cafe-freiday | Café FREIDAY Füssen Schrannengasse Bewertung klein gemütlich Sessel ... | small café, armchairs & nooks (fuessen.de blog); nothing on Kinder |
| 120 | caffe-lucca | Lucca Füssen Café Ritterstraße Bewertung Kinderwagen OR Hochstuhl ... | snippet kinderfreundlich/rollstuhlgerecht again (unverified); cash only |
| 121 | bio-cafe-baumgarten | Baumgarten Füssen Bio Café Magnusplatz Bewertung Hochstuhl OR Kinderwagen ... | interior very small, reserve; courtyard |
| 122 | konditorei-kurcafe | Konditorei Kurcafe Füssen Prinzregentenplatz Bewertung Hochstuhl OR Kinderwagen ... | snippet: kinderfreundlich, high chairs, wheelchair accessible (unverified); speisekarte.de "Familienfreundliches Restaurant"/"Terrasse" |
| 123 | alpenrose-am-see | Alpenrose am See Alpsee Hochstuhl OR Wickeltisch OR Kinderwagen OR barrierefrei ... | snippet: accessible for wheelchair users (unverified); Biergarten self-service |
| 124 | kyodai-fuessen | Kyōdai Füssen Luitpoldstraße Kinderwagen OR barrierefrei ... | familienfreundlich, Terrasse (speisekarte.de-type); Familien Essen Friday |
| 125 | beim-ditsch | Beim Ditsch Füssen Drehergasse Kinderwagen OR Hochstuhl ... | nothing |
| 126 | haus-der-gebirgsjaeger | Haus der Gebirgsjäger Füssen Spielplatz Indoor Kinder Hochstuhl Kinderkarte ... | indoor+outdoor playground, kids menu (tripadvisor snippet); 20 min walk from centre |
| 127 | markthalle-fuessen | Markthalle Füssen Schrannengasse Bewertung Kinderwagen OR Hochstuhl ... | nothing |
| 128 | stegos-fuessen | Taverna Stego's Füssen Brunnengasse Bewertung Kinderwagen OR Hochstuhl ... | nothing |
| 129 | wok-in-fuessen | Wok In Füssen Reichenstraße 33 Bewertung Kinderwagen OR Hochstuhl ... | nothing |
| 130 | il-pescatore-fuessen | Il Pescatore Füssen restaurant trip.com OR wanderlog OR yelp "high chairs" ... | trip.com id 19120662 found |
| 131 | schlossbackstube-cafe-eis | Schlossbackstube Schwangau Bäckerei Café Eis Kinderwagen OR Hochstuhl ... | nothing |
| 132 | schwansee-kiosk | Schwansee Kiosk Schwangau HappyCow OR Facebook Bewertung Kinder Sitzplätze ... | seating, lawn; nothing on Hochstuhl |
| 133 | schlossbrauhaus-schwangau | Schlossbrauhaus Schwangau Wickeltisch OR Wickelkommode OR Wickelraum Baby Toilette | nothing new (FamilyGuide already: Wickelkommode vorhanden) |
| 134 | mauchers | Maucher's Restaurant Hopfen am See Höhenstraße Bewertung Baby OR Kleinkind ... | nothing new |
| 135 | louis-ii-ruebezahl | Hotel Das Rübezahl Schwangau Restaurant Louis II Baby OR Kleinkind ... | nothing new |
| 136 | restaurant-ludwigs | Restaurant Ludwigs Füssen Reichenstraße Bewertung Baby OR Kleinkind ... | Terrasse/Wintergarten; nothing on Hochstuhl |
| 137 | restaurant-mueller-hohenschwangau | Hotel Müller Hohenschwangau Restaurant Acht-Eck Bistro Bewertung Baby ... | kids' meals; takeaway bistro; nothing on Hochstuhl |
| 138 | berggasthaus-bleckenau | Berggasthaus Bleckenau Bewertung Baby OR Kleinkind ... | bus hourly; open 10-17:30; nothing on Hochstuhl |
| 139 | gasthof-krone | Gasthof Krone Füssen Schrannengasse Bewertung Baby OR Kleinkind OR Kinderwagen ... | TRIPADVISOR REVIEW SNIPPET: stroller rejected from dining room, could eat if stroller left outside ("babies are not welcome") — snippet only |
| 140 | la-perla-fuessen | La Perla Ristorante Pizzeria Füssen Drehergasse Bewertung Baby OR Kleinkind ... | snippet: Kinderportionen, Hochstühle (unverified) |
| 141 | annapurna-fuessen | Annapurna Füssen Kemptener Straße Bewertung Baby OR Kleinkind ... | parking in front; nothing new |
| 143 | (multi:schwanen,hechten,ritterstuben,krone) | Gasthof Krone Fussen tripadvisor review stroller "not welcome" ... | review not surfaced again |
| 144 | zum-hechten | Zum Hechten Füssen Restaurant Wickeltisch OR Hochstuhl OR ... | snippet: "restaurant has high chairs (Hochstühle)" (source unverified) |
| 145 | (area) | Füssen Restaurant Wickeltisch Baby wickeln Altstadt ... | nothing |
| 146 | (area) | Hohenschwangau Wickeltisch Baby wickeln Restaurant Café Alpsee Kainz Alpenrose Ticketcenter Toiletten | Kainz Kinderkarte; nothing on Wickeltisch |
| 147 | gasthaus-zum-schwanen | Gasthaus zum Schwanen Füssen Wickeltisch OR Wickelmöglichkeit OR Kinderkarte ... | nothing (wikipedia article on building) |
| 148 | ritterstuben | Ritterstuben Füssen Wickeltisch OR Kinderkarte ... glutenfrei | CLOSURE: last day 2025-10-29/30 (findmeglutenfree/fuessenaktuell), new tenant; official article 2025-06-01: "Bis zum 30. Oktober werden sie die „Ritterstuben" noch betreiben." |
| 149 | madame-pluesch | Madame Plüsch Füssen Wickeltisch OR Kinderkarte ... | TA review title snippet: Kinderkarte vorhanden |
| 150 | hotel-hirsch | Hotel Hirsch Füssen Restaurant Wickeltisch OR Wickelraum OR Kinderkarte ... barrierefrei | official: "Reisen für alle" zertifiziert, "teilweise barrierefrei für Menschen mit Gehbehinderung" (VERIFIED fetch hotelhirsch.de/hotel/hotel-hirsch) |
| 151 | restaurant-cafe-kainz | Café Kainz OR "Restaurant Kainz" Hohenschwangau Wickeltisch OR Toiletten OR Kinderwagen OR barrierefrei ... | snippet: rollstuhlgerechter Parkplatz/Eingang; reopened 2024-03-28 (waf-bayern.de) |
| 152 | schlossrestaurant-neuschwanstein | Schlossrestaurant Neuschwanstein OR "Zur Neuen Burg" Hohenschwangau Hochstuhl OR Wickeltisch ... | nothing (bistro page: nothing) |
| 153 | alpenrose-am-see | Alpenrose am See OR "Schloss Bräustüberl" Hohenschwangau AMERON Wickeltisch OR Wickelraum OR Hochstuhl ... | hohenschwangau.de WC page: "WC next to the Schloss-Bräustüberl ... For people with disabilities and parents with infants, a separate toilet and changing table are available" (VERIFIED fetch); EUR 1.00, EU key |
| 154 | cafe-bistro-seaside | Cafe Bistro Seaside OR "Seaside Hopfensee" kids OR children OR "high chair" ... | wheelchair accessible (snippet); Facebook closure post (Nov) — seasonal? |
| 155 | ritterstuben | Ritterstuben Füssen geschlossen 2025 neue Leitung Nachfolger ... | Facebook group: "unter neuer Leitung"; findmeglutenfree: new owners early 2026 keep gluten-free menu |
| 156 | cafe-bistro-seaside | Seaside Hopfensee Café Bistro geschlossen 2025 OR 2026 Winterpause ... | official "wir haben für dich geöffnet!"; hours Mo-Sa 11-23, So 9-23 (oeffnungszeitenbuch) |
| 157 | zum-hechten | Zum Hechten Füssen Hochstühle Kinder Restaurant speisekarte OR yelp OR restaurantguru ... | snippet again: high chairs listed (source unverified) |
| 158 | alpenrose-am-see | AMERON Neuschwanstein Alpsee Resort Wickeltisch OR "changing table" ... | hotel: cribs on request; nothing on Wickeltisch |
| 159 | wirtshaus-weinbauer | yelp "S´Wirtshaus im Weinbauer" ... "Good for Kids" OR kids | snippets: high chairs available; review "separates kids and dogs into a back end room" |
| 160 | cafe-freiday | yelp "Cafe Freiday" ... "Good for Kids" OR "Wheelchair Accessible" | nothing |
| 161 | caffe-lucca | yelp "Caffé Lucca" ... "Good for Kids" OR "Wheelchair Accessible" OR "Outdoor Seating" | TA snippet: Outdoor Seating, Wheelchair Accessible |
| 162 | bio-cafe-baumgarten | yelp "Bio Cafe Baumgarten" Füssen "Good for Kids" OR "Wheelchair Accessible" ... | Yelp snippet: good for kids; NOT wheelchair accessible; outdoor seating |
| 163 | markthalle-fuessen | yelp OR restaurantguru "Markthalle" Füssen ... | nothing |
| 164 | stegos-fuessen | restaurantguru OR yelp "Stego's" Füssen ... | nothing |
| 165 | schlossbackstube-cafe-eis | restaurantguru "Schlossbackstube" OR "Cafe Sauerwein" Schwangau ... | nothing |
| 166 | wok-in-fuessen | restaurantguru OR yelp "Wok In" Füssen ... | trip.com id 19121335 found → curl: Accessibility / High chairs / Kid-friendly (VERIFIED) |
| 167 | schwansee-kiosk | restaurantguru "Schwanseekiosk" ... | restaurantguru snippet: outdoor seating, takeaway, wheelchair accessible; 4.9/235 |
| 168 | hotel-alatsee | restaurantguru OR yelp "Alatsee" ... | hotel: cribs, kids meals (kayak/trip.com) |
| 169 | alpenrose-am-see | restaurantguru OR yelp "Alpenrose am See" Schwangau ... | nothing |
| 170 | berggasthaus-bleckenau | restaurantguru OR yelp "Bleckenau" ... | nothing |
| 171 | ritterstuben | Ritterstraße 4 Füssen Restaurant neu 2026 "Ritterstuben" ... neue Pächter | new owners since beginning 2026; gluten-free menu kept, separate kitchens (findmeglutenfree snippet) |
| 172 | (area-JP) | フュッセン レストラン ベビーカー 赤ちゃん 子連れ ブログ ... | 4travel Q&A general; 1week-europe blog on Schwanen (no baby info) |
| 173 | (area-JP) | ホーエンシュヴァンガウ 子連れ ベビーカー ランチ ... | nothing (Tokyo results) |
| 174 | gasthof-krone | Gasthof Krone Füssen "stroller" OR "pram" OR "Kinderwagen" review | review not surfaced again |
| 175 | restaurant-cafe-kainz | Café Kainz ... Wickeltisch OR "changing table" OR Hochstuhl ... | nothing new |
| 176 | gasthof-krone | Gasthof Krone Füssen Wickeltisch OR "changing table" ... | nothing |
| 177 | restaurant-ludwigs | Ludwigs Füssen Hotel Restaurant Wickeltisch OR ... | nothing |
| 178 | restaurant-mueller-hohenschwangau | Hotel Müller Hohenschwangau Wickeltisch OR ... | kids' meals; nothing new |
| 179 | schneiderhanser-hotel-helmer | Hotel Helmer Schwangau Schneiderhanser Wickeltisch OR ... | nothing |
| 180 | berggasthaus-bleckenau | Bleckenau Schwangau Berggasthaus Wickeltisch OR ... | nothing |
| 181 | haus-der-gebirgsjaeger | Haus der Gebirgsjäger Füssen Wickeltisch OR ... | playground snippet again; nothing on Wickeltisch |
| 182 | kyodai-fuessen | Kyodai OR "Kyōdai" Füssen Wickeltisch OR ... | nothing (product noise) |
| 183 | il-pescatore-fuessen | Il Pescatore Füssen Wickeltisch OR ... | nothing (product noise) |
| 184 | beim-ditsch | Beim Ditsch OR "Lila Haus" Füssen Wickeltisch OR ... | nothing |
| 185 | annapurna-fuessen | Annapurna Füssen Wickeltisch OR ... | nothing (product noise) |
| 186 | caffe-lucca | Caffè Lucca Füssen Wickeltisch OR ... | nothing |
| 187 | konditorei-kurcafe | Kurcafe OR "Kurcafé" OR "Schlosskrone" Füssen Wickeltisch OR ... | snippet: "According to a menu listing, Kurcafe has highchairs available" (unverified) |
| 188 | cafe-bistro-seaside | Seaside Hopfen am See Hochstuhl OR Kinderstuhl OR ... | nothing |
| 189 | (multi:markthalle,stegos,freiday) | Markthalle Füssen OR "Stego's" Füssen OR "Café FREIDAY" Füssen Hochstuhl OR ... | nothing; Freiday "only accessible on foot" |
| 190 | (multi:schlossbackstube,schwansee) | Schlossbackstube Schwangau OR "Schwansee Kiosk" Schwangau Hochstuhl OR ... | nothing new |
| 191 | (multi:alpenrose,schlossrestaurant) | Alpenrose am See OR "Schlossrestaurant Neuschwanstein" Hohenschwangau Hochstuhl OR ... | nothing new ("perfect family dining" trip.com review) |
| 192 | zum-hechten | Zum Hechten Füssen "Hochstühle" OR "high chairs" Restaurant Ritterstraße 6 | speisekarte.menu snippet: amenities incl. high chairs, wheelchair accessibility, family-friendly (page itself JS-only, 5.6 KB) |
| 193 | wirtshaus-weinbauer | Weinbauer Schwangau Wirtshaus "Hochstühle" OR "high chairs" Füssener Straße 3 | snippet: high chairs available (menu-world.com / restexpert type listing) |
| 194 | konditorei-kurcafe | Kurcafe Füssen Prinzregentenplatz "Hochstühle" OR "high chairs" Konditorei | snippet: familienfreundlich, Terrasse, "high chairs are available" |
| 195 | cafe-freiday | Freiday Füssen Café "Hochstühle" OR "high chairs" OR "kinderfreundlich" ... | nothing |
| 196 | ritterstuben | Ritterstuben Füssen 2026 neuer Betreiber Wiedereröffnung ... | new owners since early 2026 (no names) |
| 197 | gasthof-krone | Gasthof Krone Füssen Bewertung Kinderwagen draußen stehen lassen Gaststube Baby Tripadvisor | stroller review not surfaced again (HolidayCheck/TA/RG links only) |
| 198 | zum-hechten | speisekarte.menu "Zum Hechten" Füssen Ausstattung Hochstühle rollstuhlgerecht kinderfreundlich | speisekarte.menu snippet (3rd time): Hochstühle, rollstuhlgerecht, kinderfreundlich, glutenfrei |
| 199 | fruehlingsgarten | Frühlingsgarten Füssen Bad Faulenbach Restaurant Hochstuhl OR Hochstühle OR Kinderstuhl OR Kinderkarte OR Kinderwagen | speisekarte.menu/11880-type snippet: "Hochstühle available, suitable for families" (unverified page body) |
| 200 | alpenrose-am-see | Alpenrose am See Hohenschwangau Kinderwagen OR Rollstuhl Terrasse Zugang Stufen ... | Marco Polo/outdooractive snippet: "für Rollstuhlfahrer zugänglich"; nothing on Kinderwagen/Hochstuhl |
| 201 | wirtshaus-weinbauer | Wirtshaus im Weinbauer Schwangau Kinder Hochstuhl Hinterzimmer Nebenraum ... | speisekarte.menu snippet: high chairs, family-friendly, three rooms |

（#142 は Trip.com の curl 取得の記録で WebSearch ではないため除外。#143〜#201 の番号は通し番号のまま）
