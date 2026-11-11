# 『鳥の言葉』TEI・IIIF調査と設計

更新日: 2026-10-13  
対象: ファリードゥッディーン・アッタール『鳥の言葉』（*Manṭiq al-ṭayr*）

## 1. 結論

2026年10月25日までの最小成果物は、「25対句の出典明示TEI」「TEI P5公式スキーマと独自規則の検証結果」「公開写本候補のIIIF閲覧」「設計・権利・未検証事項の文書」とするのが現実的である。

重要な原則は、テキスト、写本画像、校異、翻訳の根拠を分離することである。電子テキス間の相違を写本異読として表示せず、写本の対応葉と行領域が確認できるまで本文に`@facs`を付けない。この「未確定を未確定として符号化する」方針自体が、公募で説明できる品質管理実績になる。

## 2. 現行規格

### TEI

- 現行公閏版は[TEI P5 4.12.0（2026-07-28）](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/TitlePageRecto.html)。
- [Verse章](https://tei-c.org/release/doc/tei-p5-doc/en/html/VE.html)は`<lg>`による定型的な行群、`<l>`による詩行、`<seg>`による行内分割を提供する。
- [Critical Apparatus章](https://tei-c.org/release/doc/tei-p5-doc/en/html/TC.html)は`<app>`、`<lem>`、`<rdg>`、`<listWit>`と、location-referenced / double-end-point-attached / parallel segmentationの3方式を定義する。
- [Linking, Segmentation, and Alignment章](https://tei-c.org/release/doc/tei-p5-doc/en/html/SA.html)の`@corresp`と`<linkGrp>`を原文・翻訳対応に利用できる。
- [Representation of Primary Sources章](https://tei-c.org/release/doc/tei-p5-doc/en/html/PH.html)の`<facsimile>` / `<surface>` / `<zone>`とテキスト側の`@facs`が、頁・行領域と本文を接続する。
- [Manuscript Description章](https://tei-c.org/release/doc/tei-p5-doc/en/html/MS.html)の`<msDesc>`により、所蔵、請求記号、物質、手、装飾、来歴を記述できる。

### IIIF

- IIIF公式一覧では[Presentation API 3.0.0とImage API 3.0.0が現行安定版](https://iiif.io/api/)である。
- [Presentation API 3.0](https://iiif.io/api/presentation/3.0/)はManifest / Canvas / AnnotationPage / AnnotationとWeb Annotationにより複合オブジェクトの提示をモデル化する。
- [Image API 3.0](https://iiif.io/api/image/3.0/)は画像の領域、大きさ、回転、品質、形式をURLで指定する。
- [IIIF Cookbookの右開き例](https://iiif.io/api/cookbook/recipe/0010-book-2-viewing-direction/)に従い、ペルシア語写本のManifestは`viewingDirection: "right-to-left"`を確認対象とする。
- [外部AnnotationとManifestの接続例](https://iiif.io/api/cookbook/recipe/0306-linking-annotations-to-manifests/)に従い、行領域はCanvasの`xywh`セレクタで指定し、`partOf`でManifestへ戻れる構造にする。

## 3. ペルシア・イラン語文献の実装例

| 事例 | 技術的特徴 | 本プロジェクトへの示唆 |
|---|---|---|
| [Persian Digital Library](https://persdigumd.github.io/PDL/downloads.html) | TEI-XMLを正本とし、EpiDoc方針、`cRefPattern`、CapiTainS用メタデータを採用。CC BY-SA 4.0。 | 安定引用と機械処理を同時に設計する先行例。 |
| [Corpus Avesticum Berolinense](https://www.geschkult.fu-berlin.de/en/e/iranistik/forschung/CAB/projektbeschreibung/index.html) | 写本記述と一次資料転記の二層をTEIで記述し、独自スキーマ、eXist-db、XSLT/XQueryを採用。 | 「写本そのものの記述」と「知的内容」を分ける設計の直接的参考。 |
| [Perseus Shahnameh experimental edition](https://github.com/gregorycrane/Shahnameh) | ペルシア語原文・訳・語彙の対応と、Cambridge Shahnama ProjectのIIIF Manifest・行番号メタデータを接続しようとする実験。 | 本文版間のズレがボトルネックになること、IIIFメタデータの行番号が接続鍵になることを示す。 |
| [OpenITI Digital Publications](https://openiti.org/projects/Digital_Editions.html) | アラビア語・ペルシア語写本をOpenITI mARkdown MSSで出版する。TEI以外の軽量マークアップ路線。 | TEIは唯一の方法ではない。複雑な校異・多言語対応・写本記述を優先する本件でTEIを選ぶ理由を明確化できる。 |
| [TEI Publisher](https://www.tei-publisher.com/index.html) | TEIからの閲覧・注釈・並行表示用の汎用基盤。 | 短期は静的デモ、中期はTEI Publisherを公開基盤の候補とする。 |

### 評価

『鳥の言葉』そのものの公開TEI・IIIF統合校訂版は、今回の調査範囲では確認できなかった。したがって、本試作は完成例の複製ではなく、ペルシア語TEIコーパス、イラン語写本校訂、『王書』のIIIF実験から設計要素を組み合わせる。

## 4. 『鳥の言葉』向けTEI設計

### 4.1 対句と半句

**採用案:** 1 baytを`<lg type="couplet">`、二つのmiṣrāʿを順番付き`<l n="a|b">`とする。対句と各半句に`xml:id`を付ける。

**理由:** 対句単位の引用を保ちながら、半句単位の翻訳・校異・画像領域対応ができる。TEI公式例でも`lg type="couplet"`は使われる。

**不採用案:** 1 baytを1つの`<l>`とし、二半句を`<seg type="hemistich">`にする。この案はTEIの「詩行内の半行」例に忠実だが、ペルシア詩の左右半句の表示・引用・行領域対応が一段複雑になる。両方がTEI上は可能であり、全体の校訂方針確定時に再評価する。

### 4.2 話者と発話

**採用案:** 登場主体を`<listPerson>` / `<person xml:id>`で管理し、明示的な発話範囲に`<sp who="#hoopoe">`と`<speaker>`を用いる。語りのレベルや焦点化は`@ana`で管理し、人物の「言葉」と「語りの声」を同一視しない。

**不採用案:** すべての対句に簡易な`@who`を付ける。話者が解釈的に推定される箇所で過度に確定的になる。

### 4.3 入れ子状の物語

**採用案:** `<div type="frame|episode|anecdote">`を入れ子化し、物語上の親子関係をXMLの階層で表す。複数の分類軸（例: 登場人物、主題、語りの水準）は`@ana`と`<taxonomy>`で外付けする。

**不採用案:** 物語タグを本文に重複して入れる。XMLは交差する階層を直接入れ子にできないため、交差する分類はstand-offに逃がす。

### 4.4 異読と校訂

**採用案:** 語句レベルの非交差異読はインラインparallel segmentationとし、証人は`msDesc/@xml:id`で定義する。採用本文を決めない段階では`<app><rdg wit>...<rdg wit>...</app>`、校訂上のlemmaを選ぶ段階では`<lem>`を用いる。FSC-MS-28との最初の実例では非選択的方式を採用した。

**移行条件:** 複雑な交差異読、削除・加筆層、写本ごとの転記を扱う段階で、個別転記＋stand-off apparatusへ移行する。

**不採用案:** 出典不明の異表記を`<rdg>`にする。今回見つかったWikisourceとGanjoorの差（例: 第9対句「بگداخت / بگذاشت」）は、写本証言でなく電子テキスト間の差なので校異装置に入れない。

### 4.5 翻訳対応

**採用案:** ペルシア語本文と日本語訳を独立した`<text xml:lang>`として`<group>`に収め、`<linkGrp type="translationAlignment">`で対句または半句IDを対応させる。

**理由:** 語順の違いによる1:1以外の対応と、将来の複数訳を表せる。

**不採用案:** 各半句の直後に訳を入れる。閲覧は簡単だが、原文と訳の独立性、複数訳、非1:1対応が弱い。

### 4.6 識別子

**採用案:** 内部の`xml:id`は意味の変化しにくい`mt.0001`, `mt.0001.a`型とする。公開後はGitHub Pages等のHTTPS URIに解決し、リリース単位にZenodo DOIを付ける。人物・著作にVIAF / Wikidata等の外部URIを併記する。

**不採用案:** 章題や話者名のみでIDを作る。改題、転写、多言語化で不安定になる。

## 5. IIIF対応資料

### 5.1 使用可能性が高い資料

**Smithsonian National Museum of Asian Art, FSC-MS-28**

- [オブジェクト頁](https://asia-archive.si.edu/object/FSC-MS-28/)
- [検証済みIIIF Manifest](https://ids.si.edu/ids/manifest/FS-8501_25)
- 16世紀、イラン、インクと彩色、紙、FSC-MS-28。
- ManifestはPresentation API 2系の表現で、確認できたCanvasは1つ。完本全体のManifestとは確認できない。
- オブジェクト頁に「CC0」と「Usage Conditions Apply」の表示が併存する。デモでは元Manifestを読み込むのみとし、画像の複製再配布前に対象画像の個別表示を再確認する。

### 5.2 補助資料

**Library of Congress, PK6451.F4 M28 1933**

- [書誌・デジタル資料頁](https://www.loc.gov/item/2016397471/)
- 1933年Lucknow刊のペルシア語石版印刷、318画像。写本ではないが、連続頁のIIIFテストとテキスト位置同定に有用。
- 目録はIIIF Manifestの存在と、パブリックドメインまたは既知の制限なしで自由に再利用できることを表示する。
- 推定Manifest URLは自動検証環境でHTTP 403となったため、閲覧デモの既定資料にはしない。

### 5.3 現時点では使えない重要写本

**British Library, Add MS 7735**

- [目録](https://searcharchives.bl.uk/catalog/032-002559771)
- 15世紀末〜16世紀初、208葉の写本で、挿絵葉情報も詳細。
- 旧Digitised Manuscriptsの画像は現在利用不可と目録に明記されるため、短期デモの対象から外す。

## 6. 2026年10月25日までの最小成果物

### 完成定義

1. 20〜30対句のペルシア語TEIに出典、編集状態、安定IDがある。
2. XML構文、TEI P5 Relax NG、独自Schematronの3段階がすべて成功し、機械可読レポートが保存される。
3. IIIF Manifestを一般的なビューアで読み込める。
4. 本文と画像の対応は、実証済みの範囲だけが符号化される。対応未定でも「デモは動くが本文対応は未検証」と明示できれば最小成果物の条件を満たす。
5. README、設計書、出典・権利表、再現手順がある。

### 日程

| 期限 | 作業 | 完了判定 |
|---|---|---|
| 10/13 | 規格・事例・資料調査、25対句試作、検証基盤 | 本報告と現在のリポジトリ |
| 10/14–16 | 研究者が使用底本・範囲・正書法・話者区分を承認 | 意思決定ログ |
| 10/17–19 | 承認済み本文と日本語訳に置換、必要な話者・物語階層を付与 | TEI・Schematron再検証 |
| 10/20–21 | 対応葉の手作業同定、可能な場合は行領域座標を収録 | 根拠付き対応表 |
| 10/22–23 | 英語README、技術報告、公募用記述、画面キャプチャ | 第三者が再実行できる |
| 10/24 | 最終検証とバージョン付与 | v0.1.0候補 |
| 10/25 | 応募用の説明文を確定 | 「実装済/未検証」を分けた記述 |

## 7. AIと研究者の分担

| AIが実行できる作業 | 研究者が決める作業 |
|---|---|
| 公式仕様と公開資料の調査、リンク・版の記録 | 何を研究上の本文とするか（底本・校訂版） |
| 確定済み資料のXML/JSONへの変換 | 異読の評価、lemmaの選択、誤植と異読の判別 |
| ID付与、整形、一貫性チェック | bayt / miṣrāʿの学術的単位と番号の最終承認 |
| TEI RNG、Schematron、JSON構文の自動検証 | 話者、焦点化、物語階層の解釈 |
| IIIF Manifest解析、Canvas表の生成、領域候補の作成 | 該当葉・行の本文同定と、座標の学術的承認 |
| 既存翻訳と原文の対応候補 | 日本語訳の学術的適切性と翻訳単位 |
| README、データ辞書、検証レポートの生成 | 公開できるテキスト・訳文・画像の権利判断 |
| 公募文と面接Q&Aの草案 | 実績の寄与、責任、完成度の最終表現 |

## 8. 現在の試作と検証結果

- 初期段階ではWikisource冒頭25対句を構造検証に用いたが、第三者テキストのライセンスを本プロジェクトのCC BY 4.0と混同しないため公開対象から除外した。
- `schema/mantiq.sch`: 対句番号、2半句、a/b順、ID、出典、校異根拠を検査。
- `scripts/validate.py`: XML / TEI P5 4.12.0 Relax NG / Schematronの3段階検証。
- 初期参照試料の検証報告は、同試料とともに公開対象から除外した。
- `iiif/manifest-registry.json`: 取得確認、版、Canvas数、権利表示、本文対応状態のレジストリ。
- `viewer/index.html`: TEI本文をXMLから読み込み、BnF Persan 348のManifestと並置するMirador 3デモ。外交的転写、正規化候補、半句画像領域を切り替えて確認できる。
- ブラウザ上でManifest読込、実画像表示、サムネイル選択、ズーム操作を確認した。内部環境情報を含む動作確認JSONは公開対象から除外した。
- `outputs/project-overview-en.md`: 公募・国際発信用の英語プロジェクト概要。

### 8.1 IIIF閲覧デモの実動作確認（2026-10-13）

- ローカルHTTPサーバー上の`viewer/index.html`をCodexアプリ内ブラウザで開いた。
- TEI XMLから25対句・50半句が動的に読み込まれ、安定ID付きの本文として表示された。
- 「葉・行対応は未確認」「並置表示のみ」という警告が画面上に表示された。
- Mirador 3はSmithsonianの`FS-8501_25` Manifestを読み込み、`1 of 1 • image FS-8501_25`と表示した。
- 装丁表紙の実画像とサムネイルが表示された。
- サムネイル選択後の画像描画と、画像中央のダブルクリックによる拡大表示を目視で確認した。
- ブラウザコンソールに警告・エラーは検出されなかった。
- 検証済みタブはユーザーが確認できるよう保持した。

### 8.2 BnF Persan 348への更新（2026-10-13）

- 1492年書写のBnF Persan 348を、写本転写練習の第一候補として追加した。
- BiblissimaのTifyビューアとローカルのMirador 3でGallica IIIF Manifestを読み込んだ。
- ビューア上で223画像を確認し、scan f6の装飾見開きと冒頭ペルシア語本文を表示した。
- scan f20でも判読可能な本文見開きを確認した。
- ローカルデモの既定画像をBnF Persan 348へ変更し、TEI 25対句と写本画像を並置した。
- scan f6と現在の25対句は対応する可能性が高いが、研究者による逐語照合前のため`@facs`はまだ付与していない。
- Smithsonian FSC-MS-28の検証結果は、単一画像IIIFの比較例としてレジストリに残した。

## 9. 未完了・未検証

1. 25対句は研究者が採用する校訂版・写本と照合していない。
2. 日本語訳は未収録。AI生成訳を典拠なしで補わない。
3. 話者・物語階層はモデルのみで、試料の冒頭賛歌に実タグを付けていない。
4. 実写本に基づく`<app>` / `<rdg>`は1件のみであり、本格的な批判校訂ではない。
5. Persan 348の60半句とIIIF Canvas / `xywh`は対応済み。FSC-MS-28は最初の異読箇所について画像領域候補を記録した。
6. Library of CongressのManifest URLは、コマンドラインに加えブラウザでもCloudflareのセキュリティ検証により自動取得できなかった。カタログがManifestの存在を表示することと、Manifest本体の解析済みは区別する。
7. GitHub・Zenodoへの公開は行っていない。外部公開は別途承認後に行う。

## 10. 面接で説明できる技術的要点

- TEIは「見た目」ではなく「研究上の構造と根拠」を記述する。
- TEI P5公式スキーマ検証と、プロジェクト独自のSchematron検証は役割が違う。前者はTEI文法、後者は「対句は必ず2半句」等の実装方針を検査する。
- IIIF Presentation APIはページと表示順をCanvasで表し、Image APIはピクセル画像の取得を担う。
- TEIの`@facs`はIIIF Canvasまたは領域にリンクできるが、「技術的にリンクできる」ことと「本文対応が学術的に確定した」ことは別である。
- AIは変換・検証・候補生成に強いが、lemma、話者、物語階層、翻訳の学術的責任は研究者に残る。

