# 『鳥の言葉』Persan 348 TEI・IIIF試作 技術報告

作成日：2026年11月10日  
版：0.2.0（プロジェクト担当研究者が写本画像と照合した小規模試料。外部査読済みを意味しない）

## 1. 概要

本試作は、ファリードゥッディーン・アッタール『鳥の言葉』（*Manṭiq al-ṭayr*）の写本BnF Persan 348を対象に、ペルシア語詩の外交的転写をTEI P5で構造化し、IIIF画像の該当領域と接続するものである。目的は批判校訂版の完成ではなく、写本転写、正規化、画像対応、規格変換、検証を一貫して説明・再実行できる小規模なデジタル人文学成果物を構築することにある。

対象はscan f6〜f7上の21対句・42半句である。本文の読み、`<unclear>`を付与しない判断、3箇所の検索用正規化、全42半句の画像領域について研究者が写本画像を確認した。

## 2. 資料と学術的位置づけ

- 所蔵：Bibliothèque nationale de France, Département des Manuscrits
- 請求記号：Persan 348
- Gallica ARK：`ark:/12148/btv1b10091505x`
- 書写年：1492年4月8日
- 試料画像：Gallica IIIFのscan f6・f7
- 試料範囲：冒頭21対句・42半句

Persan 348は、TEI・IIIF実装と写本転写の練習に採用した一証人であり、最良写本、校訂底本または刊本の代替として選定したものではない。本試作の本文はPersan 348の外交的転写であって、複数証人を統合した校訂本文ではない。

## 3. データモデル

### 3.1 詩節構造

1対句（*bayt*）を`<lg type="couplet">`、二つの半句（*miṣrāʿ*）を`<l n="a">`と`<l n="b">`で表す。各対句と半句に安定した`xml:id`を付与した。この設計により、対句単位の引用と半句単位の画像・翻訳・注釈対応を両立できる。

### 3.2 外交的転写と正規化

写本の読みを既定値とし、検索・比較に必要な局所的正規化だけを`<choice><orig>…</orig><reg>…</reg></choice>`で併記した。正規化済み箇所は次の3件である。

1. `خیمه برپای` → `خیمهٔ برپای`
2. `بی ستون` → `بی‌ستون`
3. `مهره انجم` → `مهرهٔ انجم`

正規化は補助記号、分かち書き、Unicode字形統一に限定し、語彙、語順、文法解釈は変更しない。IIIF注釈へは`reg`ではなく`orig`を出力する。

### 3.3 画像対応

TEIの二つの`<surface>`がscan f6・f7の座標空間3669×2787を表し、各`<zone>`が半句領域を矩形座標で記録する。各`<l>`は`@facs`で対応する`zone`を参照し、各`surface/@corresp`がIIIF Canvas URIを示す。

BnF Manifest内の正式なCanvasは次のURIである。

`https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f6`

`https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f7`

42個の`zone`をIIIF Presentation API 3の42個のWeb Annotationへ変換し、Canvas URIに`#xywh=x,y,w,h`を付けて対象領域を表した。AnnotationPageはCanvasごとに分け、f6用24件とf7用18件を生成した。

## 4. システム構成

| 層 | 成果物 | 役割 |
|---|---|---|
| 学術データ | `data/tei/bnf-persan-348-f6-sample.xml` | 本文構造、写本記述、編集方針、画像領域 |
| TEIカスタマイゼーション | `schema/mantiq.odd` | 使用するTEIモジュールと設計理由 |
| 専用スキーマ | `schema/mantiq.rng` | ODDから生成したプロジェクト用Relax NG |
| 制約 | `schema/mantiq.sch` | プロジェクト固有の構造・参照規則 |
| 相互運用 | `iiif/bnf-persan-348-f6-annotations.json`、`bnf-persan-348-f7-annotations.json` | Canvas別の半句転写と画像領域 |
| 変換 | `scripts/tei_to_iiif_annotations.py` | TEIからCanvas別IIIF AnnotationPageを決定論的に生成 |
| スキーマ生成 | `scripts/build_odd_schema.py` | ODDから専用Relax NGを再生成しJingで検証 |
| 検証 | `scripts/validate.py` | XML、TEI All、ODD生成Relax NG、Schematron検証 |
| 相互照合 | `scripts/validate_iiif_annotations.py` | TEI本文・zoneとIIIF注釈の一致確認 |
| 表示 | `viewer/index.html` | TEI本文、領域画像、Mirador写本表示 |

## 5. 検証結果

2026年11月11日時点の結果は次のとおりである。

- XML整形式：合格
- 公式TEI P5 All Relax NG：合格
- ODD生成プロジェクト専用Relax NG：合格
- プロジェクトSchematron：合格
- 対句数：21
- 半句数：42
- 半句の`@facs`：42件すべて付与・参照解決
- IIIF Canvas：2件
- IIIF AnnotationPage：2件
- IIIF Annotation：42件
- Annotation本文とTEI外交的転写：42件すべて一致
- AnnotationのCanvas領域とTEI `zone`：42件すべて一致
- 研究者による本文確認：42半句
- 研究者による画像領域確認：42領域

機械検証はXML文法、TEI文法、プロジェクト規則、ファイル間の一致を確認する。一方、文字の読みや領域の学術的妥当性は自動検証できないため、研究者確認を別に記録した。

## 6. AIと研究者の責任分担

AIに委任した作業は、仕様調査、転写候補、座標候補、XML・JSON生成、識別子付与、規格変換、検証コード、閲覧画面、文書草案である。これらは規則化または反復可能で、機械検証や研究者の標本検査が可能である。

研究者が判断した事項は、対象写本の採用目的、文字の読み、分かち書き、対句の組合せ、`<unclear>`の要否、正規化範囲と正規化形、画像領域の妥当性である。異読評価、lemma選択、話者・物語階層、翻訳、公開上の権利判断も研究者の責任範囲に残る。

技術的専門性はXMLをすべて手入力することではなく、データモデル、規格間の役割、AIに委任できる範囲、必要な制約、検証の限界を理解し、学術判断を管理できることに置く。

## 7. 実装済み・未実装の区別

### 実装・確認済み

- Persan 348の21対句・42半句について、プロジェクト担当研究者が写本画像と照合した外交的転写
- 対句・半句構造と安定ID
- 3箇所の研究者承認済み正規化
- 42半句と42画像領域のTEI `@facs`対応
- 2 Canvasに対応するIIIF Presentation 3 AnnotationPageへの自動変換
- ODD、専用Relax NG、公式TEI All、Schematron、TEI–IIIF相互照合
- 外交的転写・正規化切替と領域表示を備えた閲覧画面

### 未実装または未検証

- 複数写本を用いた批判校訂と`<app>/<lem>/<rdg>`
- 日本語訳と原文の対応
- 話者・物語階層の実データへの適用
- 20〜30対句以上への試料拡張
- 永続的な公開URI、GitHub公開、Zenodo DOI
- Gallica画像そのものの再配布

## 8. 規格上の説明

[TEI P5](https://tei-c.org/release/doc/tei-p5-doc/en/html/)は本文の論理構造、写本記述、編集判断、責任表示を担う。[IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/)はCanvasとWeb Annotationにより画像上の位置と外部コンテンツを結び付ける。[IIIF Image API](https://iiif.io/api/image/3.0/)は画像領域の取得を担う。したがってTEIとIIIFは競合する規格ではなく、本文中心の記述と画像中心の提示を相互補完する。

## 9. 結論

本試作により、プロジェクト担当研究者が写本画像と照合した転写をTEIで構造化し、IIIF Canvas上の画像領域へ接続し、別規格へ自動変換して相互照合する一連のワークフローを実装した。成果は小規模であるが、典拠、編集状態、AI利用、研究者判断、検証範囲、未実装事項を区別しており、別の写本・作品へ再適用可能な方法論的試作となっている。
