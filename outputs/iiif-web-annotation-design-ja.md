# Persan 348・FSC-MS-28：TEIからIIIF Web Annotationへの変換設計

作成日：2026年11月10日  
更新日：2026年11月12日
状態：3 Canvas・78半句の変換・相互照合済み

## 目的

TEI内の`l/@facs → zone`対応を、IIIF対応ツールが利用できるAnnotationPageとして外部化する。これにより、TEIは本文構造と編集判断の正本、IIIF注釈はCanvas上で転写を交換する相互運用層、閲覧画面は表示層という役割分担になる。

## 採用したモデル

- 1つのTEI `l`を1つのIIIF `Annotation`へ変換する。
- `body`はプロジェクト担当研究者が写本画像と照合した外交的転写を`TextualBody`として持つ。これは外部査読済みを意味しない。
- `motivation`は、画像をCanvasへ描画する`painting`ではなく、転写を補足する`supplementing`とする。
- `target`はBnFのscan f6・f7またはSmithsonian FS-7342_15 Canvasに`#xywh=x,y,w,h`を付けた領域URIとする。
- AnnotationPageはCanvasごとに分け、`partOf`で対応Canvasを明示する。
- `choice`がある箇所では`orig`を採用し、`reg`はTEIに保持する。したがってIIIF注釈は写本転写を正規化形で上書きしない。

公式仕様：

- [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/)
- [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/)

## Canvasの確認

BnF Manifest内でscan f6・f7、Smithsonian Manifest内でFSC-MS-28冒頭画像のCanvasを確認した。

- Canvas：`https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f6`
- Canvas：`https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f7`
- Canvas：`https://ids.si.edu/ids/iiif/canvas-FS-7342_15`
- BnF寸法：3669×2787、Smithsonian寸法：2090×3520
- 各TEI `surface`寸法は対応Canvasと一致する。

CanvasとTEI surfaceが同一の座標系を使うため、`zone`を単純な`xywh`へ変換できる。

## 変換例

TEI：

```xml
<l xml:id="mt.bnf348.0001.a" facs="#bnf348.f6.z001a">آفرین جان آفرین پاک را</l>
```

IIIF注釈の主要部分：

```json
{
  "type": "Annotation",
  "motivation": "supplementing",
  "body": {
    "type": "TextualBody",
    "value": "آفرین جان آفرین پاک را",
    "format": "text/plain",
    "language": "fa"
  },
  "target": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b10091505x/canvas/f6#xywh=2350,1310,520,180"
}
```

## 検証

`scripts/validate_iiif_annotations.py`が以下を相互照合する。

1. JSONが読み込め、Presentation API 3の基本形を持つこと。
2. TEIの78半句と3 AnnotationPage内のAnnotationの件数・識別子が一致すること。
3. Annotation本文がTEIの外交的転写と一致すること。
4. Canvas領域がTEI `zone`から算出した`xywh`と一致すること。

検証結果は`outputs/iiif-annotation-validation.json`へ保存する。

## AIと研究者の境界

AIに委任できる範囲：

- `l/@facs`の解決と座標変換。
- `orig`からの外交的転写抽出。
- Canvas別AnnotationPage生成と機械的な相互照合。
- 公開URL変更時の一括再生成。

研究者が判断する範囲：

- 転写本文が写本の読みに忠実か。
- `zone`が学術的に妥当な引用領域か。
- 外交的転写、正規化、翻訳、注釈を別AnnotationPageに分ける公開方針。
- 公開URI、ライセンス表示、永続性の最終方針。

今回、本文と領域の学術判断は研究者がすでに承認済みである。AIはその承認済みデータを別規格へ決定論的に変換しており、新しい本文判断は行っていない。

## 公開前の残課題

現在のAnnotationPage `id`はGitHub Pages用のHTTPS URLである。公開先を変更する場合は、次のように新しい永続的URLを指定して再生成する。

```powershell
python scripts/tei_to_iiif_annotations.py --base-url https://example.org/project
python scripts/validate_iiif_annotations.py
```

公開先の決定と公開操作は研究者の承認後に行う。
