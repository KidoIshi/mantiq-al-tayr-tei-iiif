# 転写練習候補：BnF Persan 348

確認日：2026年10月13日  
推薦状態：練習用の第一証人として研究者承認済み

## 資料概要

- 所蔵：Bibliothèque nationale de France, Département des Manuscrits
- 請求記号：Persan 348
- 作品：Farīd al-Dīn ʿAṭṭār, *Manṭiq al-ṭayr*
- 書写完了：1492年4月8日
- 書写者：Mawlānā Ḥasan-ʿAlī b. M. b. ʿAbd-ullāh Ḥamza Kātib
- 形態：213葉、ペルシア語ナスターリーク体、1頁12行・2段組
- [Biblissima資料ページ](https://iiif.biblissima.fr/collections/manifest/cb11f0b6f2ee91a4ef6c400c66b5bba416cfd217)
- [Gallica資料ページ](https://gallica.bnf.fr/ark:/12148/btv1b10091505x)
- [IIIF Manifest](https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/manifest.json)
- [Gallica利用条件](https://gallica.bnf.fr/edit/und/conditions-dutilisation-des-contenus-de-gallica)

## 技術的確認

- BiblissimaのTifyビューアでManifestが読み込まれた。
- ビューアは223画像を表示した。
- scan `f6`で装飾された冒頭見開きとペルシア語本文を目視確認した。
- scan `f20`でも判読可能な本文見開きを目視確認した。
- IIIF Image APIによる幅1000px画像取得を確認した。
- ローカルのMirador 3でもManifest、223画像、scan 6の本文画像を表示できた。
- ローカル画面ではTEI 25対句と写本画像を同時表示できる。

確認用画像URI：

- scan f6: <https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/f6/full/1000,/0/native.jpg>
- scan f20: <https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/f20/full/1000,/0/native.jpg>

## 学習対象として適している理由

1. 一冊の写本全体をIIIF Presentation APIで扱える。
2. Image APIを使って同じ画像を異なる解像度や領域で取得できる。
3. 冒頭本文が現在のTEI試料と対応する可能性があり、転記比較を始めやすい。
4. 見開き、二段組、写本上の行、対句・半句の関係を検討できる。
5. `pb`、`lb`、`facsimile`、`surface`、`zone`、`@facs`を実例で学べる。
6. 後に別写本や刊本と比較して校異へ拡張できる。

## 現時点で確定していないこと

- scan f6の各行と、現在のWikisource由来25対句の逐語対応。
- 写本の葉番号とManifest上のscan番号の正確な対応規則。
- 各対句を写本のどの行・画像領域へ結びつけるか。
- 文字の判読、異綴り、省略、訂正の最終判断。
- Gallica画像を成果物へ複製収録する場合の利用条件。現段階では画像を複製せず、IIIF URIを読み込む。

## 採用後の最初の実習

1. scan f6の最初の2〜5対句について、AIが写本転写候補を作る。
2. 研究者が原画像と比較し、正しい読み・不確実箇所を判断する。
3. 写本転写を現在の参照本文とは別レイヤーでTEI化する。
4. 行領域の`xywh`候補をAIが作成する。
5. 研究者が画像領域との対応を承認する。
6. TEI Relax NGと独自Schematronで再検証する。

## 研究者に必要な判断

この写本を最初の練習対象として採用するかを判断する。採用は、この写本を最良写本または校訂上の底本と認定することを意味しない。短期のTEI・IIIF実習に使用する一証人としての採用である。
