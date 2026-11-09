# 再現・検証手順

作成日：2026年11月10日

## 1. 必要環境

- Python 3.10以上（作成環境はPython 3.12.10）
- `lxml`（作成環境は6.1.3）
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

1. TEIから18件のIIIF Annotationを再生成する。
2. XML整形式、TEI Relax NG、Schematronを検証する。
3. IIIF Annotation本文・識別子・Canvas領域をTEIと相互照合する。
4. 総合結果を`outputs/project-verification-summary.json`へ保存する。

成功時は`"all_passed": true`となる。

## 3. 個別実行

TEI検証：

```powershell
python scripts/validate.py --offline `
  --tei data/tei/bnf-persan-348-f6-sample.xml `
  --report outputs/validation-report-bnf348-f6.json
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

- 左側に9対句・18半句が表示される。
- 「写本どおり」と「正規化候補」を切り替えられる。
- 半句を選択すると右上の画像領域が切り替わる。
- 「IIIF注釈を開く」から18件のAnnotationPageを取得できる。
- MiradorにBnF Persan 348のManifestが読み込まれる。

## 5. 期待される検証値

| 項目 | 期待値 |
|---|---:|
| 対句 | 9 |
| 半句 | 18 |
| IIIF Annotation | 18 |
| XML整形式 | true |
| TEI Relax NG | true |
| Schematron | true |
| TEI本文との一致 | true |
| zoneとの一致 | true |
| エラー | 0 |

## 6. 公開時の変更

現在のAnnotationPage `id`はローカル用の`http://127.0.0.1:8000/`である。公開先が確定したら、永続的なHTTPS URLを指定して再生成する。

```powershell
python scripts/tei_to_iiif_annotations.py `
  --base-url https://公開先.example/project
python scripts/validate_iiif_annotations.py
```

公開後は、AnnotationPageのURLが実際にJSONを返すこと、画像利用条件をREADMEに表示すること、公開版にバージョンを付けることを確認する。

## 7. 再現できる範囲とできない範囲

第三者は、ファイル生成、XML・スキーマ検証、TEI–IIIF相互照合、閲覧画面の動作を再現できる。一方、ペルシア語の読み、正規化の妥当性、画像領域が対象半句を適切に囲むかという学術判断は、機械検証だけでは再現できない。これらはTEIの責任表示、変更履歴、確認文書によって判断過程を追跡できるようにしている。
