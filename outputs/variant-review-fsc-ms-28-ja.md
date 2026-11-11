# 第二写本FSC-MS-28：校異候補確認票

作成日：2026年11月11日  
状態：公式メタデータ・IIIF画像確認済み、本文読みは研究者確認待ち

## 1. 資料

- 所蔵：Smithsonian National Museum of Asian Art, Freer Study Collection
- 請求記号：FSC-MS-28
- 作品：Farīd al-Dīn ʿAṭṭār, *Manṭiq al-ṭayr*
- 年代：16世紀（所蔵機関メタデータ）
- 地域：Iran（所蔵機関メタデータ）
- [公式オブジェクトページ](https://asia.si.edu/explore-art-culture/collections/search/edanmdm:fsg_FSC-MS-28/)
- [冒頭頁画像のIIIF Manifest](https://ids.si.edu/ids/manifest/FS-7342_15)
- [冒頭頁全体](https://ids.si.edu/ids/iiif/FS-7342_15/full/1600,/0/default.jpg)
- [第4対句付近の拡大画像](https://ids.si.edu/ids/iiif/FS-7342_15/150,1800,1150,480/full/0/default.jpg)

公開されているのは全冊分の連続Manifestではなく、表紙・冒頭頁・挿絵頁など7点の個別画像Manifestである。画像自体はリポジトリへ複製せず、SmithsonianのIIIF URIを参照する。オブジェクトページとManifestは`Usage Conditions Apply`を表示しているため、将来の公開時にも出典と利用条件へのリンクを明示する。

## 2. 採用理由

`FS-7342_15`は作品冒頭頁を含み、Persan 348で研究者確認済みの第1対句以降と同一箇所を比較できる。したがって、電子本文同士の差ではなく、独立した二写本の画像に基づく最小校異例を作成できる。

この採用はFSC-MS-28を最良写本、校訂底本、または完全な比較証人と認定するものではない。公開画像で確認できる冒頭範囲だけを第二証人として用いる。

## 3. 最初の差異候補

| 対句・半句 | Persan 348 | FSC-MS-28のAI転写候補 | 状態 |
|---|---|---|---|
| 0004b | وین دگر را دایما آرام داد | وان دگر را دایما آرام داد | FSC-MS-28の冒頭語を研究者確認待ち |

確認点は、FSC-MS-28の冒頭語を`وان`と読んでよいかである。Persan 348の`وین`はすでに研究者承認済みであり、今回の確認対象ではない。

## 4. TEI設計案

### 推奨：採用本文を決めない並列読み

```xml
<app type="variant">
  <rdg wit="#wit-bnf348">وین</rdg>
  <rdg wit="#wit-fsc28">وان</rdg>
</app> دگر را دایما آرام داد
```

この方式では、二写本のどちらを優れた読みとするかをまだ決めず、各読みと証人の対応だけを記録する。現在のPersan 348転写画面とBnF用IIIF Annotationには`#wit-bnf348`の読みだけを出力し、比較表示では両方を提示する。

### 代案：Persan 348を表示上の基準として`lem`にする

```xml
<app type="variant">
  <lem wit="#wit-bnf348">وین</lem>
  <rdg wit="#wit-fsc28">وان</rdg>
</app> دگر را دایما آرام داد
```

この方式は処理が単純だが、`lem`が「校訂上より正しい読み」と誤解される可能性がある。Persan 348は練習用の第一証人であって最良写本とは認定していないため、現段階では非選択的な`rdg`併記を推奨する。

## 5. AIと研究者の役割

AIが行う作業：

- 公式メタデータとIIIF Manifestの取得・解析。
- 対応箇所と異読候補の抽出。
- `msDesc`、`app/rdg`、画像領域、変換・表示・検証コードの実装。
- 二写本の読みと画像座標の機械的整合性検査。

研究者が行う作業：

- FSC-MS-28の冒頭語を`وان`と読んでよいかの画像確認。
- 差を写本異読として採用するかの判断。
- 将来lemmaを選ぶ場合の本文批判上の評価。

読みが承認された後、AIがTEIへの第二写本記述、非選択的校異装置、FSC-MS-28画像領域、閲覧画面の比較表示、Schematron規則、検証結果を一括実装する。
