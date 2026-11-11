# 再現・検証手順

作成日：2026年11月10日

## 1. 必要環境

- Python 3.10以上（作成環境はPython 3.12.10）
- Java 17以上（Jingによる専用Relax NG検証に使用）
- `lxml`、SaxonC、Jing（`requirements.txt`から導入）
- 閲覧画面ではインターネット接続が必要

PowerShellでプロジェクト直下へ移動し、依存関係を導入する。

```powershell
python -m pip install -r requirements.txt
```

## 2. 全検証の一括実行

```powershell
python scripts/verify_all.py
```

このコマンドは次を順番に行う。

1. ODDからプロジェクト専用Relax NGを再生成し、ODDと試料をJingで検証する。
2. TEIから60件のIIIF Annotationを、2 Canvasに対応する2個のAnnotationPageとして再生成する。
3. XML整形式、公式TEI All、ODD生成Relax NG、Schematronを検証する。
4. IIIF Annotation本文・識別子・Canvas領域をTEIと相互照合する。
5. 総合結果を`outputs/project-verification-summary.json`へ保存する。

成功時は`"all_passed": true`となる。

## 3. 個別実行

TEI検証：

```powershell
python scripts/validate.py --offline `
  --tei data/tei/bnf-persan-348-f6-sample.xml `
  --report outputs/validation-report-bnf348-f6.json
```

ODDから専用スキーマを再生成：

```powershell
python scripts/build_odd_schema.py
```

IIIF AnnotationPage再生成：

```powershell
python scripts/tei_to_iiif_annotations.py
```

TEI–IIIF相互照合：

```powershell
python scripts/validate_iiif_annotations.py
```

## 4. 閲覧画面

```powershell
python -m http.server 8000
```

ブラウザで`http://127.0.0.1:8000/viewer/`を開く。確認項目は次のとおりである。

- 左側に30対句・60半句が表示される。
- 「写本どおり」と「正規化候補」を切り替えられる。
- 半句を選択すると右上の画像領域が切り替わる。
- f6・f7の注釈リンクから、24件と36件のCanvas別AnnotationPageを取得できる。
- MiradorにBnF Persan 348のManifestが読み込まれる。

## 5. 期待される検証値

| 項目 | 期待値 |
|---|---:|
| 対句 | 30 |
| 半句 | 60 |
| IIIF Canvas | 2 |
| IIIF AnnotationPage | 2 |
| IIIF Annotation | 60 |
| XML整形式 | true |
| 公式TEI All Relax NG | true |
| ODD生成Relax NG | true |
| Schematron | true |
| TEI本文との一致 | true |
| zoneとの一致 | true |
| エラー | 0 |

## 6. 公開時の変更

現在のAnnotationPage `id`はGitHub Pages用のHTTPS URLである。公開先を変更する場合は、新しい永続的URLを指定して再生成する。

```powershell
python scripts/tei_to_iiif_annotations.py `
  --base-url https://公開先.example/project
python scripts/validate_iiif_annotations.py
```

公開後は、AnnotationPageのURLが実際にJSONを返すこと、画像利用条件をREADMEに表示すること、公開版にバージョンを付けることを確認する。

## 7. 再現できる範囲とできない範囲

第三者は、ファイル生成、XML・スキーマ検証、TEI–IIIF相互照合、閲覧画面の動作を再現できる。一方、ペルシア語の読み、正規化の妥当性、画像領域が対象半句を適切に囲むかという学術判断は、機械検証だけでは再現できない。これらはTEIの責任表示、変更履歴、確認文書によって判断過程を追跡できるようにしている。
