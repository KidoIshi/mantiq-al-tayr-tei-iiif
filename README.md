# Manṭiq al-ṭayr TEI・IIIF 試作

『鳥の言葉』（*Manṭiq al-ṭayr*）を対象に、TEI P5でのペルシア語韻文構造化とIIIF連携を検証するための最小試作です。

研究者：石川 喜堂（Kido Ishikawa）  
[ORCID](https://orcid.org/0009-0009-2254-2189)・[researchmap](https://researchmap.jp/kidoishi/)

リポジトリ：`https://github.com/KidoIshi/mantiq-al-tayr-tei-iiif`

## 現在の到達点

- Persan 348の12対句を収録した、TEI P5 4.12.0に対して検証可能な小規模写本転写
- 対句（`lg`）と半句（`l`）の安定識別子
- 出典、編集状態、変更履歴、再利用条件の明記
- TEI ODDによる使用モジュールの形式化と専用Relax NGスキーマの再生成
- プロジェクト独自Schematron規則
- 確認済みIIIF ManifestのレジストリとMirador閲覧デモ
- TEI本文とIIIF画像を並置し、外交的転写と正規化候補を切り替える閲覧画面
- プロジェクト担当研究者が画像と照合した24半句をCanvas領域へ結び付けたIIIF Presentation 3 AnnotationPage
- TEIからAnnotationPageを再生成し、本文・座標の一致を機械検証するスクリプト
- 調査・設計・短期実装計画（日本語）
- 公募・国際発信用の英語プロジェクト概要

## ディレクトリ

```text
data/tei/bnf-persan-348-f6-sample.xml BnF写本転写（担当研究者が画像と照合した12対句）
outputs/research-and-design-ja.md 調査・設計報告
outputs/project-overview-en.md    英語プロジェクト概要
outputs/editorial-decision-log-ja.md 編集判断ログ
outputs/learning-roadmap-ja.md      技術習得ロードマップ
outputs/ai-human-boundary-map-ja.md AI委任境界マップ
outputs/manuscript-candidate-bnf-persan-348-ja.md BnF写本候補評価
outputs/transcription-review-bnf348-f6-ja.md 写本転写確認票
outputs/diplomatic-normalization-design-ja.md 外交的転写・正規化併存設計
outputs/iiif-zone-alignment-design-ja.md TEI半句と画像領域の対応設計
outputs/iiif-web-annotation-design-ja.md IIIF Web Annotation変換設計
outputs/iiif-annotation-validation.json IIIF注釈の検証記録
outputs/odd-customization-design-ja.md ODD設計・レビュー教材
outputs/odd-build-report.json      ODD生成・検証記録
outputs/odd-negative-test-report.json ODDが未採用モジュールを拒否する反例検査
outputs/technical-report-ja.md 担当研究者が画像と照合した試料の技術報告
outputs/reproducibility-guide-ja.md 第三者向け再現・検証手順
outputs/project-verification-summary.json 全検証の総合結果
iiif/manifest-registry.json      IIIF資料候補と確認状態
iiif/bnf-persan-348-f6-annotations.json 24半句のIIIF AnnotationPage
schema/mantiq.sch                独自Schematron規則
schema/mantiq.odd                プロジェクト専用TEI ODD
schema/mantiq.rng                ODDから生成した専用Relax NG
scripts/build_odd_schema.py      ODDから専用スキーマを再生成
scripts/test_odd_schema.py       TEI Allと専用スキーマの差を反例で検査
scripts/validate.py              XML / TEI RNG / Schematron検証
scripts/tei_to_iiif_annotations.py TEIからIIIF注釈への変換
scripts/validate_iiif_annotations.py TEIとIIIF注釈の相互照合
scripts/verify_all.py            全生成・検証の一括実行
scripts/check_release_readiness.py 公開前の不足事項を機械確認
viewer/index.html                TEI・IIIF並置閲覧デモ
```

## 検証

Python 3、Java 17以降、`lxml`、SaxonC、Jingを用います。初回のみ、固定したTEI P5 4.12.0およびTEI Stylesheets 7.61.0の公式資源を`work/`へ取得します。

```powershell
python -m pip install -r requirements.txt
python scripts/build_odd_schema.py
```

`build_odd_schema.py`は`schema/mantiq.odd`から`schema/mantiq.rng`を生成し、ODD自体とPersan 348試料をJingで検証します。

```powershell
python scripts/validate.py
```

オフライン再検証は、一度キャッシュを作成した後に次のように行います。

```powershell
python scripts/validate.py --offline
```

IIIF注釈の再生成と相互照合は次のとおりです。

```powershell
python scripts/tei_to_iiif_annotations.py
python scripts/validate_iiif_annotations.py
```

全処理を一括して再実行する場合は次のコマンドを使います。

```powershell
python scripts/verify_all.py
```

検証は三つの役割を分けています。

- 公式`tei_all.rng`：TEI P5全体に対する適合性
- ODD生成`mantiq.rng`：本プロジェクトが選択したTEIモジュールに対する適合性
- `mantiq.sch`：二半句、ID規則、画像参照などのプロジェクト固有条件

技術的な公開条件の不足は次のコマンドで確認できます。著者・ライセンス・公開URIが未決定の間は、意図的に不合格になります。この検査は、第三者資料の権利処理や学術的妥当性の判断を代替しません。

```powershell
python scripts/check_release_readiness.py
```

AnnotationPageの`id`は公開予定のGitHub Pages URLを使用します。公開先を変更する場合は`--base-url`で置換し、再生成します。

## IIIFデモ

```powershell
python -m http.server 8000
```

その後、`http://localhost:8000/viewer/`を開きます。外部CDNとBnF GallicaのManifestを読み込むためネットワークが必要です。

## 重要な制限

- Persan 348試料の本文読み12対句と全24半句の`zone`座標は、プロジェクト担当研究者が写本画像と照合して確認しています。これは外部査読済みであることを意味しません。
- 正規化形は検索・比較用の試験候補であり、刊本本文や批判校訂本文ではありません。
- 異読・話者・日本語訳のモデルは設計済みですが、研究者による典拠確認前のデータは未投入です。
- IIIF AnnotationPageはPresentation API 3の基本構造に基づき、TEIとの本文・識別子・画像座標の一致をプロジェクト独自の規則で検証しています。Presentation API全体に対する公式適合性検査を主張するものではありません。

## ライセンス

- 本プロジェクト作成のTEIデータ、IIIF Annotation、検証結果、文書： [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Python、HTML、JavaScript、Schematron、GitHub Actions：MIT License
- BnF/Gallica画像：リポジトリへ複製せずIIIF URIを参照。出典は「Source gallica.bnf.fr / Bibliothèque nationale de France」。画像再利用は[Gallicaの利用条件](https://gallica.bnf.fr/accueil/fr/html/conditions-dutilisation-de-gallica)に従います。

詳細は`LICENSE`と`LICENSE-CODE`を参照してください。

