# 公開前に研究者が決定する事項

更新日：2026年11月10日

技術的な公開準備は自動化できるが、次の内容は研究者本人が決定する。決定後、AIが`CITATION.cff`、`LICENSE`、TEIヘッダー、公開用URI、READMEへ一括反映する。

## 1. 公開上の著者名

- 日本語表記：石川 喜堂
- ローマ字表記：Kido Ishikawa
- 所属：記載なし（researchmapの基本情報に現在の正式所属が明示されていないため、担当科目の大学名から推定しない）
- ORCID：0009-0009-2254-2189
- researchmap：`https://researchmap.jp/kidoishi/`

## 2. 公開物の名称

暫定案：

- 日本語：『鳥の言葉』Persan 348 TEI・IIIF写本転写試作
- 英語：*Manṭiq al-ṭayr*: A TEI–IIIF Manuscript Transcription Prototype for BnF Persan 348

## 3. ライセンス

暫定推奨案：

- TEIデータ・IIIF Annotation・文書：CC BY 4.0（研究者承認済み）
- Python・HTML・Schematronコード：MIT License（研究者承認済み）
- BnF画像：リポジトリへ複製せず、GallicaのIIIF URIを参照。画像利用はGallicaの条件に従う。

ライセンス選択は、所属機関の方針とGallicaの利用条件を確認したうえで研究者が承認する。

## 4. GitHub公開先

- GitHubユーザー名：`KidoIshi`
- リポジトリ名：`mantiq-al-tayr-tei-iiif`
- GitHub Pagesを利用するか：未決定

GitHub Pagesを利用する場合、そのURLをIIIF AnnotationPageの永続的な`id`として使用する。

## 5. バージョン

最初の公開版は`v0.1.0`とし、「研究者確認済み9対句・18半句の小規模試作」と明記する案を採用する。20〜30対句への拡張後は`v0.2.0`とする。

## 6. DOI

GitHubの最初のRelease作成後にZenodoへ登録し、版固有DOIと全版共通Concept DOIを記録する。DOI取得後、`CITATION.cff`、README、TEI `publicationStmt`へ反映する。
