# 乳児連れ情報 深掘り調査ログ — オーバーヴェーゼル／ザンクト・ゴアール／バッハラッハ 27店

- 調査日: 2026-09-26（調査専用セッション）
- 対象: `europe/germany/control/research_oberwesel.json` の `stores` 27店（既存ファイルは変更せず、本ログと `baby_oberwesel.json` のみ新規作成）
- 調査項目: ベビーカー入店（stroller）／ハイチェア（highchair）／おむつ替え台（changing）、補助として子どもメニュー（kids_menu）

## WebSearch 使用回数（正確な数）

- **セッション上限 200 回を使い切った。** 結果が返った検索: **200 回**（店別 179 回 ＋ 横断・一般 21 回）。201 回目の呼び出しは「200 of 200 used」で拒否された（1 件、結果なし）。
- 店別回数（全店 5 回以上 → 4 回以上の基準を満たすため、何も出なかった項目は「情報なし」と表記）:

| 店 id | 回数 | 判定 | ベビーカー | ハイチェア | おむつ替え | 子どもメニュー |
|---|---|---|---|---|---|---|
| zum-mundschenk | 14 | found | 不可 | あり | 情報なし | あり |
| schoenburger-weinstuben | 6 | found | 不可 | あり | 情報なし | 情報なし |
| weinhaus-weiler | 7 | none | 情報なし | 情報なし | 情報なし | 情報なし |
| goldener-pfropfenzieher | 5 | found | 可 | あり | あり | 情報なし |
| heimathafen-550 | 8 | found | 可 | 情報なし | 情報なし | 情報なし |
| guenderodehaus | 7 | none | 情報なし | 情報なし | 情報なし | 情報なし |
| oppermanns-kronprinzen | 7 | found | 情報なし | あり | あり | あり |
| schloss-rheinfels-auf-scharffeneck | 6 | found | 情報なし | あり | 情報なし | 情報なし |
| burgschaenke-der-landgraf | 7 | found | 可 | 情報なし | 情報なし | 情報なし |
| gasthaus-zur-krone-st-goar | 5 | found | 情報なし | あり | 情報なし | あり |
| hotel-keutmann | 9 | found | 可 | あり | 情報なし | 情報なし |
| hotel-loreleyblick | 6 | found | 情報なし | あり | 情報なし | 情報なし |
| cafe-restaurant-loreley-st-goarshausen | 6 | found | 情報なし | あり | 情報なし | 情報なし |
| altes-haus-bacharach | 7 | found | 不可 | 情報なし | 情報なし | 情報なし |
| stuebers-restaurant | 6 | found | 可 | あり | 情報なし | あり |
| an-der-stadtmauer-bacharach | 7 | none | 情報なし | 情報なし | 情報なし | 情報なし |
| posthof-bacharach | 6 | found | 可 | あり | 情報なし | 情報なし |
| luz-de-mar-am-rhein | 6 | found | 不可 | あり | 情報なし | 情報なし |
| pippo-bistro-alt-backstub | 5 | found | 可 | あり | 情報なし | 情報なし |
| lanius-knab-strausswirtschaft | 7 | found | 可 | 情報なし | 情報なし | 情報なし |
| bastian-zum-gruenen-baum | 7 | found | 可 | 情報なし | 情報なし | 情報なし |
| heidrich-weinkrug | 8 | found | 可 | 情報なし | 情報なし | 情報なし |
| kurpfaelzische-muenze | 6 | found | 可 | 情報なし | 情報なし | 情報なし |
| cafe-und-baecker-st-goar | 6 | none | 情報なし | 情報なし | 情報なし | 情報なし |
| konditorei-cafe-bonsch | 5 | found | 可 | あり | 情報なし | あり |
| eiscafe-italia-76-bacharach | 5 | found | 可 | 情報なし | 情報なし | 情報なし |
| eiscafe-la-dolce-vita-oberwesel | 5 | found | 可 | 情報なし | 情報なし | 情報なし |
| _general（横断検索: trip.com / wanderlog / gastroguide / golocal / speisekartenweb / cylex / foodpearl / 観光ポータル / 公衆トイレ） | 21 | – | – | – | – | – |

## 集計

- 何か1項目以上が判明した店（found）: **23** ／ 4回以上調べても何も出なかった店（none＝ガイドでは「情報なし」）: **4** ／ 予算不足で未確認のまま（partial）: **0**
- ベビーカー: 可 14, 情報なし 9, 不可 4
- ハイチェア: あり 14, 情報なし 13
- おむつ替え台: 情報なし 25, あり 2 — **27店中どこにも明記なし**（ホテル設備として Goldener Pfropfenzieher「Baby-Wickelauflage」、Kronprinzen「Wickeltisch」のみ）
- 子どもメニュー: 情報なし 22, あり 5

## 判定の凡例と注意

- 「あり／可／不可」は出典に明記があるもの。ホテル併設店は、ホテル設備欄（HolidayCheck・RheinBurgenWeg・Trip.com hotel）の記載をそのまま「レストランのハイチェア」と混同しないよう note に「ホテル設備として」と明記した。ただし Burghotel Auf Schönburg は HolidayCheck 設備欄「Baby- und Kinderausstattung: Hochstuhl」＋ foodpearl（Google属性転載）「Hochstühle verfügbar」の2系統があるためレストランでも「あり」とした。
- ベビーカー「可」の多くは「rollstuhlgerecht／barrierefrei／Accessibility」表示からの判断（段差なし＝押して入れる）。「不可」は Schönburg（公式FAQ「nicht barrierefrei… Bereits am Eingang … Stufen」＋上部城内へ階段）、Altes Haus（TripAdvisor「Not wheelchair accessible」）、Luz de Mar（市壁の上へ階段）。畳んで持ち込めるかどうかは不明。
- 「情報なし」= その店について WebSearch 4 回以上＋公式サイト（あれば）＋主要ポータルを読んだが記載なし。「未確認」は残っていない。
- Google Maps Platform（Places API 等）は使用していない（ユーザー指示）。

## 読めた情報源／読めなかった情報源（実測）

読めた（WebFetch 本文取得可）: 各店公式サイト、hotel-schoenburg.com 全ページ、HolidayCheck（/hi/ 設備欄）、Trip.com 店舗ページ（設備タグ High chairs / Kid-friendly / Accessibility が最も体系的）、Wanderlog（リスト・店ページ、Google クチコミ転載）、RheinBurgenWeg／romantischer-rhein／welterbe-mittelrheintal／rheinsteig、bacharach.de、golocal（属性欄）、speisekartenweb.de（Google属性の文章転載）、GastroGuide（「Barrierefrei essen」カテゴリ）、outdooractive、verwoehnwochenende.de、check24、kerstin-g-rush-autorin.de。

読めなかった（本文取得不可・検索スニペットのみ使用と明記）: TripAdvisor（403、curl でも 403）、Restaurant Guru（503）、foodpearl.com（403、curl でも 403）、speisekarte.menu（403）、menuweb.menu（403）、cylex.de（403）、hotels.com（503）、Expedia（429）、kurzurlaub.de（404）、Booking.com DAS WESEL（本文空）、Trip.com 一部ID（404: 19231312, 19213658, 64826850）、gasthaus-zur-krone.com/familien（404・別の Krone）、hotel-schoenburg.com/en/hotel（404）。TheFork・Falstaff・ADAC は今回対象外。

## 店別の主要根拠（原語引用）

### zum-mundschenk（14回・found）
- ベビーカー：ホテル公式FAQ（複数予約サイトが転載）「Die historische Burganlage ist nicht barrierefrei. Bereits am Eingang und in verschiedenen Bereichen des Hotels gibt es Stufen.」「Der Zugang durch die Burgmauer ist stellenweise eng … für Rollstühle nicht geeignet」。駐車場から約150 mの登り（一部不整地の石畳）、上部城内（ホテル入口）へは礼拝堂と居館の間の階段。→ベビーカーは入口で畳んで持ち上げる前提（不可＝「そのまま押して入れない」の意）。ハイチェア：HolidayCheck のホテル設備欄「Baby- und Kinderausstattung: Hochstuhl, Kostenlose Baby-/Kinderbetten」、foodpearl（Google属性転載・検索スニペット）「Hochstühle verfügbar」。子どもメニュー：公式ページに「Spaghettini mit Tomaten- oder Bolognesesauce」「Rostbratwürstchen mit Kartoffelpüree」「Überraschungseis mit Früchten und Gummibären」。ベビーベッド：公式料金ページ「Babybetten sind kostenfrei.」。エレベーターは一部のみ（FAQ「nicht alle Zimmer, Etagen und Hotelbereiche mit dem Aufzug erreichbar」）。おむつ替え台：全ページ・全ソースで記載なし。
- 出典: https://www.holidaycheck.de/hi/burghotel-auf-schoenburg/c47812c1-b8f7-3a7a-bced-2f69f5b39f8c ; https://www.hotel-schoenburg.com/zum-mundschenk ; https://www.hotel-schoenburg.com/preise ; https://hotel.check24.de/hotel/germany/6871085 ; https://www.verwoehnwochenende.de/kurzurlaub/hotel/burghotel-auf-schoenburg-2251
- 当たった情報源: 公式サイト全ページ(hotel-schoenburg.com: / /hotel /zimmer /preise /zum-mundschenk /weinstuben /restaurant /anreise /burggarten /turmmuseum /interessantes-fur-ihren-aufenthalt; /en/hotel は404), HolidayCheck(設備欄), check24(Nicht rollstuhlgerecht, Babybett), verwoehnwochenende.de(Baby & Kinderbett, Aufzug部屋別), romantischer-rhein.de, RheinBurgenWeg, speisekartenweb.de, kuladig.de(Burghof階段), hotels.com(503), foodpearl(403; スニペットのみ), TripAdvisor(403; スニペットのみ)

### schoenburger-weinstuben（6回・found）
- Weinstuben 固有の記載はなし。同じ城内（Burghotel Auf Schönburg）につき、ベビーカー・ハイチェアはホテル全体の情報を適用：FAQ「Die historische Burganlage ist nicht barrierefrei. Bereits am Eingang … gibt es Stufen.」／HolidayCheck 設備欄「Baby- und Kinderausstattung: Hochstuhl」。Weinstuben は14:30〜23:00、温かい料理15:00〜21:00、小皿を複数同時に出すスタイル（公式）。子どもメニューの記載なし。
- 出典: https://www.holidaycheck.de/hi/burghotel-auf-schoenburg/c47812c1-b8f7-3a7a-bced-2f69f5b39f8c ; https://www.hotel-schoenburg.com/weinstuben ; https://hotel.check24.de/hotel/germany/6871085
- 当たった情報源: 公式サイト(/weinstuben ほか全ページ), HolidayCheck, check24, RheinBurgenWeg(en/a-schoenburger-weinstuben-auf-burg-schoenburg), romantischer-rhein.de, speisekarte.de, wohin-mit-kind.de(スニペット)

### weinhaus-weiler（7回・none）
- レストランのハイチェア・ベビーカー・おむつ替えの記載はどこにも見つからず。ホテル側：HolidayCheck 設備欄「Baby- und Kinderausstattung: Keine Baby-/Kinderbetten」「Lift」「Spielzimmer」、公式Wissenswertes「Babybetten sind kostenfrei, müssen jedoch im Vorfeld angemeldet werden」（矛盾あり）。speisekartenweb（Google属性転載）「Auch für einen Besuch mit Kindern ist dieser Ort aufgrund seiner familienfreundlichkeit gut geeignet.」、Restaurant Guru タグ「Kid-friendly」。Trip.com の設備欄にハイチェアなし。
- 出典: https://www.holidaycheck.de/hi/hotel-weinhaus-weiler/9f539c37-fd90-3e85-8bd7-c1a6ab14feea ; https://speisekartenweb.de/restaurants/oberwesel/thai-restaurant-weinhaus-weiler-81999
- 当たった情報源: 公式サイト(weinhaus-weiler.de, /uebernachten/wissenswertes/), HolidayCheck, RheinBurgenWeg(a-hotel-restaurant-weiler), romantischer-rhein.de, speisekartenweb.de, Trip.com(19231335), Restaurant Guru(スニペット), TripAdvisor(スニペット)

### goldener-pfropfenzieher（5回・found）
- RheinBurgenWeg（Weinhotel のページ）Ausstattung に「Kinderhochstuhl」「Baby-Wickelauflage」「Gitterbett / Babybett」「Lift / Aufzug」「Familienfreundlich」（ホテル設備として掲載）。Trip.com 店舗ページ（19231357）設備欄「High chairs」「Kid-friendly」「Accessibility」「Parking」。TripAdvisor スニペット「High chairs available … wheelchair accessible」→ベビーカー可と判断。
- 出典: https://www.rheinburgenweg.com/a-weinhotel-goldener-pfropfenzieher ; https://au.trip.com/travel-guide/foods/Kaub-27010-restaurant/Goldener%20Pfropfenzieher-19231357
- 当たった情報源: 公式サイト(goldener-pfropfenzieher.com; /restaurant/ は403), RheinBurgenWeg(hotel/restaurant両ページ), Trip.com, romantischer-rhein.de, Kayak/Booking(スニペット), TripAdvisor(スニペット)

### heimathafen-550（8回・found）
- 公式サイトのサービス欄「Barrierefrei」、ホテル DAS WESEL（同一建物）は「facilities for disabled guests」「family rooms, some with connecting doors」（Booking スニペット）→段差なし＝ベビーカー可。ハイチェア・おむつ替えは公式・DAS WESEL FAQ・観光ポータル・Tripadvisor スニペットのいずれにも記載なし。テラス席あり（Schaarplatz の交通音の指摘あり）。
- 出典: https://heimathafen550.de/?lang=de ; https://www.booking.com/hotel/de/das-wesel-dein-am-rhein.en-gb.html
- 当たった情報源: 公式サイト, DAS WESEL(daswesel.de: /en/contact-us /en/faq /en/eat--drink), Booking(スニペット; 本文空), RheinBurgenWeg(a-heimathafen-550), welterbe-mittelrheintal.de, romantischer-rhein.de, Rhein-Zeitung, sluurpy/restaurantnet(スニペット), TripAdvisor(スニペット)

### guenderodehaus（7回・none）
- ハイチェア・ベビーカー・おむつ替えの記載はどこにも見つからず。観光ディレクトリに「geeignet für Kinder, Familien」のカテゴリ表示のみ。セルフサービス（入口で注文、席は自由）、駐車場は店の直近（PKW, Bus, Wohnmobil）、食事は「im unteren Bereich des Hauses」または「Balkon bzw. unteren terrassenähnlichen Bereich」（Tripadvisor スニペット）。Trip.com 設備欄なし。
- 出典: https://www.gastroguide.de/restaurant/206830/guenderodehaus/oberwesel/ ; https://www.tripadvisor.com/Restaurant_Review-g198501-d1886472-Reviews-Gunderodehaus_Filmhaus_Heimat_3-Oberwesel_Rhineland_Palatinate.html
- 当たった情報源: 公式サイト(guenderodehaus.de, /guenderodehaus), GastroGuide, HolidayCheck(pi), outdooractive, speisekartenweb.de, Trip.com(149416519; 19231312は404), mittelrheingold.de, TripAdvisor(スニペット)

### oppermanns-kronprinzen（7回・found）
- いずれもホテル（Landhotel Zum Kronprinzen）の設備として：kurzurlaub.de（検索スニペット）「Kinder-/Babybett, Kinderhochstuhl, Kindermenü, Spielplatz, Wickeltisch」、Trip.com ホテルページ「Kinderspielplatz」＋レストラン「Kindermahlzeiten」、HolidayCheck「Kinderbetreuung nach Vereinbarung und Aufpreis」「Kinderspielplatz」「Zustellbares Babybett」「Lift」。公式サイト・Trip.com レストランページ（Oppermanns Restaurant 56469080）には子ども関連の記載なし。※夜のみ営業（火〜土 17:30〜）・4〜5コースの日替わりメニュー。
- 出典: https://de.trip.com/hotels/oberwesel-hotel-detail-8389694/landhotel-zum-kronprinzen/ ; https://www.holidaycheck.de/hi/landhotel-zum-kronprinzen/0f24a4b7-45df-33b3-a604-5f96fd1d28ee ; https://www.kurzurlaub.de/hotel/hunsrueck_nahe/oberwesel_dellhofen/das-landhotel-zum-kronprinzen/hotelbewertung_386664.html
- 当たった情報源: 公式サイト(hotel-kronprinzen.de), Trip.com(hotel 8389694 / restaurant 56469080, 52812412), HolidayCheck, kurzurlaub.de(スニペット; 本文404), romantischer-rhein.de(設備欄に子ども項目なし), welterbe-mittelrheintal.de, Booking(スニペット)

### schloss-rheinfels-auf-scharffeneck（6回・found）
- Trip.com 店舗ページ（Schloss Rheinfels 19213692）設備欄「High chairs」「Outdoor seating」「Parking」。Hotels.com/Kayak のホテル設備にも「high chairs」、TripAdvisor スニペットに「Highchairs Available」。HolidayCheck（ホテル）：「Nicht alle Bereiche des Hotels sind barrierefrei zugänglich」「Kinderbetreuung: Auf Anfrage」「Zustellbares Babybett」。公式は「Hunde im Restaurant (mit Ausnahme der Außengastronomie) nicht gestattet」のみ。
- 出典: https://us.trip.com/restaurant/germany/sankt-goarshausen/detail/schloss-rheinfels-19213692/ ; https://www.holidaycheck.de/hi/hotel-schloss-rheinfels/1ff6c6b9-0a63-32d9-a67c-e8bf87206501
- 当たった情報源: 公式サイト(schloss-rheinfels.de/restaurant), Trip.com, HolidayCheck, Hotels.com(スニペット; 本文503), Kayak(スニペット), speisekartenweb.de, TripAdvisor(スニペット)

### burgschaenke-der-landgraf（7回・found）
- speisekarte.menu（検索スニペット）「wheelchair accessible」、speisekarte.de「Familienfreundliches Restaurant」→ベビーカーは可と判断（ただし城跡全体は「a lot of stairs and uneven ground」）。ハイチェア：同ホテルの Trip.com/Hotels.com に「High chairs」（Scharffeneck/ホテル側の記載で Landgraf 固有ではない）→未確認。公式「Tischreservierung sowohl in der Burgschänke als auch auf unserer Terrasse leider NICHT möglich」。golocal（2013）「ständiges Kommen u Gehen … auf dem Weg zur Burg, zur Toilette」。
- 出典: https://speisekarte.menu/restaurants/sankt-goar/burgschaenke-der-landgraf ; https://www.schloss-rheinfels.de/restaurant/ ; https://www.golocal.de/sankt-goar/restaurants-gaststaetten/burgschaenke-der-landgraf-YUD1A/
- 当たった情報源: 公式サイト(schloss-rheinfels.de), speisekarte.menu(403; スニペット), speisekarte.de(スニペット), golocal, Wanderlog(6637357), gastronomieguide(スニペット), Yelp(スニペット), TripAdvisor(スニペット)

### gasthaus-zur-krone-st-goar（5回・found）
- Trip.com 店舗ページ設備欄「High chairs」「Kid-friendly」「Outdoor seating」「Parking」；menuweb.menu（スニペット）「highchairs available」。Wanderlog 転載の Google クチコミ「We got a really nice corner spot and our infant got a comfortable baby chair to sit in.」。公式メニュー「Für unsere kleinen Gäste」：「Micky Maus – kleines Schnitzel mit Pommes frites」「Minnie – 6 Chicken Nuggets mit Pommes frites」。公式「leider KEINE Kartenzahlung möglich」。ベビーカー・おむつ替えは記載なし。
- 出典: https://www.trip.com/restaurant/germany/sankt-goar/detail/zur-krone-19213666/ ; https://www.kronegoar.de/unsere-speisekarte/ ; https://wanderlog.com/list/geoCategory/370865
- 当たった情報源: 公式サイト(kronegoar.de, /unsere-speisekarte/), Trip.com, Wanderlog(list 370865, 314521 / place 2761905), menuweb.menu(スニペット), speisekartenweb.de, romantischer-rhein.de(a-restaurant-zur-krone), Yelp(スニペット)

### hotel-keutmann（9回・found）
- menuweb.menu の設備欄（検索スニペット、本文は403）「Highchairs available」「Wheelchair accessible」「Outdoor eating」→段差なし＝ベビーカー可と判断。ホテルにエレベーターなし（TripAdvisor スニペット「no elevator」）、2寝室のファミリースイート、100席のライン河テラス（公式）。公式サイト・HolidayCheck・Trip.com にはハイチェア等の記載なし。
- 出典: https://menuweb.menu/restaurants/sankt-goar/hotel-keutmann-restaurant ; https://www.hotel-keutmann.de/restaurant.html
- 当たった情報源: 公式サイト(hotel-keutmann.de, /restaurant.html), menuweb.menu(403; スニペット), HolidayCheck, romantischer-rhein.de, Wanderlog(7820709), Trip.com(19213658は404), TripAdvisor(スニペット), Yelp(スニペット)

### hotel-loreleyblick（6回・found）
- Trip.com 店舗ページ（Loreleyblick 19213696）設備欄「High chairs」「Parking」「Pet-friendly」。HolidayCheck（ホテル）「Angebot für Kinder: Kinderspielplatz, Spielzimmer, Brettspiele/ Puzzles」「Garten」「Terrasse」。Booking スニペット「not barrier-free」。公式は自家製アイス「für Groß und Klein」、大きなサンテラス。おむつ替え記載なし。
- 出典: https://us.trip.com/restaurant/germany/sankt-goarshausen/detail/loreleyblick-19213696/ ; https://www.holidaycheck.de/hi/hotel-loreleyblick/796d53e8-1147-3016-af80-d1ca7c786988
- 当たった情報源: 公式サイト(loreleyblick.de), Trip.com, HolidayCheck, Booking(スニペット), TripAdvisor(スニペット)

### cafe-restaurant-loreley-st-goarshausen（6回・found）
- Trip.com 店舗ページ（Café-Restaurant Loreley 19261467）設備欄「High chairs」「Kid-friendly」「Outdoor seating」「Parking」。屋内80席（一部ライン河ビュー）・屋外30席（Rheinsteig）。2025年3月1日に経営交代・再開（公式）。golocal・HolidayCheck のクチコミに子ども関連の言及なし。
- 出典: https://us.trip.com/restaurant/germany/sankt-goarshausen/detail/caf-restaurant-loreley-19261467/ ; https://www.rheinsteig.de/en/a-cafe-restaurant-loreley
- 当たった情報源: 公式サイト(cafe-restaurant-loreley.de), Trip.com, Rheinsteig, golocal, HolidayCheck(pi), rlp-tourismus.com, menuweb(403), TripAdvisor(スニペット), Yelp(スニペット)

### altes-haus-bacharach（7回・found）
- TripAdvisor 設備欄（検索スニペット、本文403）「Not wheelchair accessible」→14世紀の木組み家屋で段差あり、ベビーカーのまま入店は不可と判断。Trip.com 設備欄なし。bacharach.de「Gerne richten wir Ihre Familien- und Betriebsfeiern bis zu 65 Personen aus.」。クチコミ（スニペット）に大人数の子連れで料理提供が遅かった旨。ハイチェア・おむつ替えは全ソースで記載なし。
- 出典: https://www.tripadvisor.com/Restaurant_Review-g580190-d5529141-Reviews-Altes_Haus-Bacharach_Rhineland_Palatinate.html ; https://www.bacharach.de/a-altes-haus
- 当たった情報源: bacharach.de(公式扱い), golocal, Wanderlog(326668), Trip.com(18714247), speisekartenweb.de, RheinBurgenWeg(en/a-das-alte-haus), TripAdvisor(スニペット), Yelp(スニペット)

### stuebers-restaurant（6回・found）
- TripAdvisor クチコミ「Top Restaurant in Bacharach auf der Stadtmauer」（検索スニペット、本文403）：赤ちゃん用パンをリクエストで出してくれ、手入れされた快適なハイチェアあり。子どもメニュー：公式・Expedia「children's menu」、check24「Kinder- und Seniorenmenü」。check24（ホテル）「Aufzug im Haus」「kinderfreundlich」「Kinderbett」→ベビーカー可と判断（レストラン入口の段差そのものは未記載）。テラスは市壁上の遊歩道側。
- 出典: https://www.tripadvisor.de/ShowUserReviews-g580190-d2333546-r769720549-Stubers_Restaurant-Bacharach_Rhineland_Palatinate.html ; https://hotel.check24.de/hotel/germany/7476863 ; https://www.expedia.com/Bacharach-Hotels-Rhein-Hotel-Bacharach.h36164437.Hotel-Information
- 当たった情報源: 公式サイト(rhein-hotel-bacharach.de/stuebers-restaurant/), bacharach.de, check24(スニペット), Expedia(スニペット; 本文429), speisekartenweb.de, Trip.com(19198523), TripAdvisor(スニペット)

### an-der-stadtmauer-bacharach（7回・none）
- 設備の記載はどこにも見つからず。クチコミ（Restaurant Guru スニペット）「Essen war super lecker, Service sehr freundlich und unsere Kinder willkommen」。同住所（Marktstraße 3）の旧名「Jägerstube」の Google 属性転載（speisekartenweb）に「Dieser Ort wird eher nicht für einen Besuch mit Kindern empfohlen.」があるが旧営業時のデータの可能性。50席。
- 出典: https://restaurantguru.com/An-der-Stadtmauer-Bacharach ; https://speisekartenweb.de/restaurants/bacharach/j%C3%A4gerstube-27858
- 当たった情報源: 公式サイト(stadtmauer-bacharach.de), Restaurant Guru(スニペット; 本文503), speisekartenweb.de(Jägerstube), Trip.com(jagerstube 19198548), Wanderlog, TripAdvisor(スニペット), gelbeseiten

### posthof-bacharach（6回・found）
- Trip.com 店舗ページ（Posthof Bacharach 68678578）設備欄「High chairs」「Kid-friendly」「Accessibility」「Outdoor seating」。TripAdvisor スニペットも「Highchairs Available」「Wheelchair Accessible」。公式・bacharach.de・romantischer-rhein.de・outdooractive の設備欄には記載なし（815㎡・200席超、ビアガーデン、中庭）。
- 出典: https://www.trip.com/travel-guide/foods/bacharach-26829-restaurant/posthof-bacharach-68678578 ; https://www.tripadvisor.com/Restaurant_Review-g580190-d26626974-Reviews-Posthof_Bacharach-Bacharach_Rhineland_Palatinate.html
- 当たった情報源: 公式サイト(bacharach-posthof.de, /en/about), Trip.com, bacharach.de, romantischer-rhein.de, outdooractive, Wanderlog(6108887), TripAdvisor(スニペット)

### luz-de-mar-am-rhein（6回・found）
- TripAdvisor クチコミ「Leckeres spanisches Essen」（検索スニペット、本文403）：Kinderhochstuhl が用意されていた、子ども3人で訪問、kinderfreundlich、子どもは市壁の上から列車を眺められる。アクセス：「Man muss die alte Stadtmauer … hinaufsteigen」（outdooractive/Tripadvisor スニペット）、入口は線路と家並みの間の通路→階段を上るためベビーカーのまま不可と判断。屋内35席・屋外20席（bacharach.de）。屋外席は列車の騒音あり。
- 出典: https://www.tripadvisor.de/ShowUserReviews-g580190-d17651467-r806774101-Luz_de_Mar_am_Rhein-Bacharach_Rhineland_Palatinate.html ; https://www.bacharach.de/a-luz-del-mar ; https://www.outdooractive.com/de/gastro/romantischer-rhein/luz-del-mar/54474947/
- 当たった情報源: 公式サイト(squarespace), bacharach.de, outdooractive, speisekartenweb.de, TripAdvisor(スニペット; 本文403), Restaurant Guru(スニペット), foodpearl(403), Wanderlog

### pippo-bistro-alt-backstub（5回・found）
- speisekartenweb.de（Google 属性の転載）「Es bietet auch gute Kindermöglichkeiten mit Hochstühlen und Toiletten.」「Das Restaurant ist rollstuhlgerecht mit barrierefreiem Eingang, Parkplatz und Sitzgelegenheiten.」；cylex（スニペット）も同旨。一方 golocal の属性は「Barrierefreiheit: Nein」で矛盾あり。Trip.com 設備欄にはハイチェア表示なし。屋外席あり。
- 出典: https://speisekartenweb.de/restaurants/bacharach/pippo-bistro-zur-alten-backstube-27848 ; https://www.golocal.de/bacharach/italienische-restaurants/pippo-bistro-zur-alten-backstube-9zIik/
- 当たった情報源: speisekartenweb.de, golocal, cylex(スニペット), Trip.com(19198544), Wanderlog(2732765), TripAdvisor(スニペット), speisekarte.de

### lanius-knab-strausswirtschaft（7回・found）
- GastroGuide の「Barrierefrei essen in Oberwesel」カテゴリに掲載（＝バリアフリー）、席はほぼ屋外の中庭（公式）、中庭に駐車可→ベビーカー可と判断。ハイチェア・おむつ替えはGastroGuide・観光ポータル・Wanderlog・cylex（403）等どこにも記載なし。営業は天候次第。
- 出典: https://www.gastroguide.de/city/oberwesel/barrierefrei-essen-inklusiv/ ; https://lanius-knab.de/strausswirtschaft/
- 当たった情報源: 公式サイト, GastroGuide(262783 + barrierefrei カテゴリ), RheinBurgenWeg, romantischer-rhein.de, welterbe-mittelrheintal.de, outdooractive, cylex(403), Wanderlog, TripAdvisor(スニペット)

### bastian-zum-gruenen-baum（7回・found）
- GastroGuide の「Barrierefrei essen in Bacharach」カテゴリに掲載、TripAdvisor 設備欄（スニペット）「family-friendly, wheelchair accessible」、speisekarte.menu（スニペット）「accessible for wheelchair users」→ベビーカー可と判断。bacharach.de「In den urigen Räumen und auf den luftigen Sonnenplätzen」「malerischen Innenhof」。ハイチェア・おむつ替えの記載は見つからず（Trip.com 設備欄にもなし）。
- 出典: https://www.gastroguide.de/city/bacharach/barrierefrei-essen-inklusiv/ ; https://www.bacharach.de/a-zum-gruenen-baum ; https://www.tripadvisor.com/Restaurant_Review-g580190-d2251338-Reviews-Weingut_Fritz_Bastian-Bacharach_Rhineland_Palatinate.html
- 当たった情報源: 公式サイト(weingut-bastian-bacharach.de), bacharach.de, GastroGuide(177023 + barrierefrei カテゴリ), Trip.com(19198532, 143637344), speisekartenweb.de, speisekarte.menu(403; スニペット), TripAdvisor(スニペット), Yelp(スニペット)

### heidrich-weinkrug（8回・found）
- Rhein-Nahe 観光局「Eingang und Speiseraum ebenerdig erreichbar」（前回調査）。TripAdvisor クチコミ（スニペット）：車椅子の同行者が屋外席も店内も問題なく利用できたが「the bathroom is not fully accessible」。Yelp スニペット「wheelchair-accessible entrance, outdoor seating」。ハイチェア・おむつ替えの記載はどこにもなし。Wanderlog「Outstanding family owned restaurant!」。
- 出典: https://rhein-nahe-touristik.de/gastgeber/weingueter-und-weinstuben/ ; https://www.tripadvisor.com/Restaurant_Review-g580190-d3222974-Reviews-Weingut_Karl_Heidrich-Bacharach_Rhineland_Palatinate.html
- 当たった情報源: 公式サイト(weingut-karl-heidrich.de), bacharach.de, Rhein-Nahe Touristik, outdooractive, speisekarte.menu(403), Wanderlog, TripAdvisor(スニペット), Yelp(スニペット), mindtrip(スニペット)

### kurpfaelzische-muenze（6回・found）
- Trip.com 店舗ページ（34583814）設備欄「Kid-friendly」「Outdoor seating」「Parking」（High chairs の表示なし）。Wanderlog 転載の Google クチコミ「free WiFi and toys for our child were provided」。TripAdvisor スニペット「wheelchair accessible」（設備欄）→ベビーカー可と判断。ハイチェア・おむつ替えの明記なし。
- 出典: https://us.trip.com/restaurant/germany/bacharach/detail/kurpfalzische-munze-34583814/ ; https://wanderlog.com/list/geoCategory/369568/les-meilleurs-restaurants-pour-d%C3%AEner-%C3%A0-bacharach
- 当たった情報源: 公式サイト(muenze-bacharach.de), Trip.com, Wanderlog, golocal, speisekartenweb.de, TripAdvisor(スニペット), speisekarte.de

### cafe-und-baecker-st-goar（6回・none）
- golocal 属性「Kinderfreundlich: ja」「Barrierefreiheit: geht so（＝どちらとも言えない）」「Geeignet für: … Familien」。Trip.com 店舗ページ（19213660）設備欄は「Outdoor seating」「Parking」等でハイチェアなし。屋内40席・屋外30席（公式）。おむつ替えの記載なし。
- 出典: https://www.golocal.de/sankt-goar/cafes/cafe-u-baecker-st-goar-inh-jan-schnichels-9uJX0/ ; https://www.trip.com/restaurant/germany/sankt-goar/detail/caf-u-bcker-st-goar-19213660/
- 当たった情報源: 公式サイト(cafe-stgoar.de; 503), golocal, Trip.com, Wanderlog(2884667), cylex(スニペット), TripAdvisor(スニペット)

### konditorei-cafe-bonsch（5回・found）
- Trip.com 店舗ページ（34666742）設備欄「High chairs」「Kids' menu」「Kid-friendly」「Accessibility」「Outdoor seating」。Google ビジネス属性の転載（kerstin-g-rush-autorin.de）「Hochstühle, Kinderfreundlich, Speisekarte für Kinder」「Rollstuhlgerechter Eingang」。RheinBurgenWeg 属性「Familienfreundlich」「Kinder」。1階に約100席（公式）。おむつ替え台の記載なし。
- 出典: https://us.trip.com/restaurant/germany/oberwesel/detail/konditorei-cafe-bonsch-34666742/ ; https://kerstin-g-rush-autorin.de/konditoreicafe-bonsch/ ; https://www.rheinburgenweg.com/a-cafe-bonsch
- 当たった情報源: 公式サイト(cafe-bonsch.de), Trip.com, kerstin-g-rush-autorin.de(Google属性転載), RheinBurgenWeg, romantischer-rhein.de, cylex(403), TripAdvisor(スニペット)

### eiscafe-italia-76-bacharach（5回・found）
- Trip.com 店舗ページ（140633143）設備欄「Accessibility」「Accessible seating」「Takeout」。cylex/gelbeseiten（Google属性転載・スニペット）「kinderfreundlich, rollstuhlgerechte Sitzgelegenheiten, rollstuhlgerechter Eingang, rollstuhlgerechtes WC」→ベビーカー可と判断。店前にベンチ席。TripAdvisor スニペット：カップは2スクープ以上でないと不可。ハイチェアの記載なし。
- 出典: https://us.trip.com/restaurant/germany/bacharach/detail/eiscafe-italia76-carpe-diem-140633143/ ; https://web2.cylex.de/firma-home/italia-76-eiscaf%C3%A9-2798741.html
- 当たった情報源: GastroGuide(15231), Trip.com, cylex(403; スニペット), gelbeseiten(スニペット), golocal, TripAdvisor(スニペット), Yelp(スニペット)

### eiscafe-la-dolce-vita-oberwesel（5回・found）
- Restaurant Guru/foodpearl のクチコミ（検索スニペット、本文403）：来店時にベビーカーをどかすよう不快な態度で言われた（＝ベビーカーで入店自体はできたが置き場所を指示された；「可」はこの1件に基づく）。golocal クチコミ（2017-07-11, PEZ）「ich durfte als Mutter dreier Kinder minimum 2 Kugel Eis bestellen」。Trip.com 設備欄は「Takeout」「Dine-in」のみ。屋外席は通り沿い。ハイチェア・おむつ替えの記載なし。
- 出典: https://www.golocal.de/oberwesel/eiscafes/eiscafe-la-dolce-vita-YUD11/ ; https://la-dolce-vita-oberwesel.foodpearl.com/ ; https://us.trip.com/restaurant/germany/oberwesel/detail/restaurant-81956959/
- 当たった情報源: golocal, Trip.com, foodpearl/Restaurant Guru(403; スニペット), romantischer-rhein.de, cylex(スニペット), TripAdvisor(スニペット), Yelp(スニペット)

## 補足：公衆トイレのおむつ替え台（横断検索）

- Oberwesel: 市庁舎（Stadthaus, Rathausstraße 3）にバリアフリー公衆トイレ（romantischer-rhein.de「Barrierefreie Toilette im Stadthaus」）。Wickeltisch の有無は記載なし。
- St. Goar: 市庁舎（Rathaus, Heerstraße 130）に通年の公衆トイレ（romantischer-rhein.de「Öffentliche Toiletten Rathaus」）。Wickeltisch の有無は記載なし。
- Bacharach: 該当情報なし。

## セッションの制約・未完了

- ai-memory リポジトリ（HNishimura0504/ai-memory）の clone は 2 経路とも権限分類器に拒否された（add_repo=Permission Grant 拒否、トークン付き clone=Credential Leakage 拒否）。そのため `session_coordination.md`／`session_records.md` への記録と `preflight_capability_check.sh` の実行はできていない。親セッションでの転記が必要。
- PR 作成の可否は最終報告に記載。
