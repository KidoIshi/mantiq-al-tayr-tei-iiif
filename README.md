# Manṭiq al-ṭayr TEI・IIIF 試作

『鳥の言葉』（*Manṭiq al-ṭayr*）を対象に、TEI P5でのペルシア語韻文構造化とIIIF連携を検証するための最小試作です。

研究者：石川 喜堂（Kido Ishikawa）  
[ORCID](https://orcid.org/0009-0009-2254-2189)・[researchmap](https://researchmap.jp/kidoishi/)

公開予定リポジトリ：`https://github.com/KidoIshi/mantiq-al-tayr-tei-iiif`

## 現在の到達点

- TEI P5 4.12.0に対する構文・スキーマ検証が可能な参照用25対句と、Persan 348研究者確認済み9対句
- 対句（`lg`）と半句（`l`）の安定識別子
- 出典、編集状態、変更履歴、再利用条件の明記
- プロジェクト独自Schematron規則
- 確認済みIIIF ManifestのレジストリとMirador閲覧デモ
- TEI本文とIIIF画像を並置し、外交的転写と正規化候補を切り替える閲覧画面
- 研究者確認済み18半句をCanvas領域へ結び付けたIIIF Presentation 3 AnnotationPage
- TEIからAnnotationPageを再生成し、本文・座標の一致を機械検証するスクリプト
- 調査・設計・短期実装計画（日本語）
- 公募・国際発信用の英語プロジェクト概要

## ディレクトリ

```text
data/tei/mantiq-sample.xml       TEI試料（25対句）
data/tei/bnf-persan-348-f6-sample.xml BnF写本転写（研究者確認済み9対句）
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
outputs/technical-report-ja.md 研究者確認済み試料の技術報告
outputs/reproducibility-guide-ja.md 第三者向け再現・検証手順
outputs/job-application-achievement-ja.md 公募書類用の研究実績記述案
outputs/project-verification-summary.json 全検証の総合結果
iiif/manifest-registry.json      IIIF資料候補と確認状態
iiif/bnf-persan-348-f6-annotations.json 18半句のIIIF AnnotationPage
schema/mantiq.sch                独自Schematron規則
scripts/validate.py              XML / TEI RNG / Schematron検証
scripts/tei_to_iiif_annotations.py TEIからIIIF注釈への変換
scripts/validate_iiif_annotations.py TEIとIIIF注釈の相互照合
scripts/verify_all.py            全生成・検証の一括実行
scripts/check_release_readiness.py 公開前の不足事項を機械確認
viewer/index.html                TEI・IIIF並置閲覧デモ
```

## 検証

Python 3と`lxml`を用います。初回のみTEI Consortiumから公式Relax NGスキーマを`work/schema-cache/`へ取得します。

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

公開準備の不足事項は次のコマンドで確認できます。著者・ライセンス・公開URIが未決定の間は、意図的に不合格になります。

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

- `mantiq-sample.xml`はWikisourceの冒頭25対句を参照転記した構造検証用試料で、批判校訂版ではありません。
- Persan 348試料の本文読み9対句と全18半句の`zone`座標は研究者確認済みである。
- 正規化形は検索・比較用の試験候補であり、刊本本文や批判校訂本文ではありません。
- 異読・話者・日本語訳のモデルは設計済みですが、研究者による典拠確認前のデータは未投入です。

## ライセンス

- 本プロジェクト作成のTEIデータ、IIIF Annotation、検証結果、文書： [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Python、HTML、JavaScript、Schematron、GitHub Actions：MIT License
- BnF/Gallica画像：リポジトリへ複製せずIIIF URIを参照。画像再利用は[Gallicaの利用条件](https://gallica.bnf.fr/edit/und/conditions-dutilisation-des-contenus-de-gallica)に従います。

詳細は`LICENSE`と`LICENSE-CODE`を参照してください。

