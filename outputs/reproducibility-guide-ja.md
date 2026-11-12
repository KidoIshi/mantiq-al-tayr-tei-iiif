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
2. 校異装置からPersan 348とFSC-MS-28の本文を証人別に抽出できることを検査する。
3. FSC-MS-28冒頭9対句の18転写候補が、TEI内の18画像領域候補と一対一に対応することを検査する。
4. TEIからBnF 60件・FSC-MS-28 18件のIIIF Annotationを、3 Canvasに対応する3個のAnnotationPageとして再生成する。
5. XML整形式、公式TEI All、ODD生成Relax NG、Schematronを検証する。
6. IIIF Annotation本文・識別子・Canvas領域をTEIと相互照合する。
7. 総合結果を`outputs/project-verification-summary.json`へ保存する。

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

- 「Persan 348」では30対句・60半句、「FSC-MS-28」では9対句・18半句が表示される。
- 「並列比較」では冒頭9対句を二列で表示し、半句を選ぶと二写本の画像領域が同時に切り替わる。
- 「写本どおり」「正規化候補」「異読比較」を切り替えられる。
- 異読比較では0004bのPersan 348 `وین دگر`とFSC-MS-28 `وان دگر`が表示され、FSC-MS-28の画像領域候補を開ける。FSC-MS-28の`د`は点線と背景色で判読不確実と示され、「判読注」を展開するとTEIの古書体注を読める。
- 半句を選択すると右上の画像領域が切り替わる。
- f6・f7の注釈リンクから、24件と36件のCanvas別AnnotationPageを取得できる。
- MiradorにBnF Persan 348とSmithsonian FSC-MS-28の二つのManifestが読み込まれる。

## 5. 期待される検証値

| 項目 | 期待値 |
|---|---:|
| 対句 | Persan 348：30 / FSC-MS-28：9 |
| 半句 | Persan 348：60 / FSC-MS-28：18 / 合計78 |
| IIIF Canvas | 3 |
| IIIF AnnotationPage | 3 |
| IIIF Annotation | 78 |
| TEI apparatus | 1 |
| 証人別本文抽出 | Persan 348 `وین دگر` / FSC-MS-28 `وان دگر`（後者の`د`は字母単位で`unclear`） |
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
