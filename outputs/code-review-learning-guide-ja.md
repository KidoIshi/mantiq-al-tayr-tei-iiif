# 『鳥の言葉』TEI・IIIF実装　研究者向けコードレビュー教材

更新日：2026年11月13日

## 1. このレビューの目的

この教材の目的は、PythonやJavaScriptを暗記して同じコードを一から書けるようにすることではない。AIが生成・修正した実装について、研究者本人が次を説明できるようにすることである。

1. どの学術資料を入力としているか。
2. 研究上の概念を、どのTEI要素・属性で表したか。
3. TEIからIIIF表示用データがどう作られるか。
4. 各検証層が何を検出し、何を保証しないか。
5. AIへ委任できる処理と、研究者が判断すべき事項はどこで分かれるか。
6. 不具合や異議が出たとき、どのファイルへ戻ればよいか。

別のAIを用いた相互コードレビューは、バグ、保守性、セキュリティ、テスト不足を独立に調べる品質保証である。本教材はそれとは別に、研究者が設計と証拠の流れを理解するためのレビューである。両者は競合せず、相互補完する。

## 2. 全体像

```text
写本画像・IIIF Manifest
        │
        │ 研究者が読み・対句・不確実性・画像領域を承認
        ▼
data/tei/bnf-persan-348-f6-sample.xml  ← 構造化本文の正本
        │
        ├── 公式TEI P5 Relax NG ───── TEI一般への適合
        ├── schema/mantiq.rng ─────── ODDで選択した語彙への適合
        ├── schema/mantiq.sch ─────── 対句・ID・証人・座標の独自規則
        │
        ├── scripts/collate_opening_witnesses.py
        │       └── 二写本の一致・異読・欠損の比較結果
        │
        └── scripts/tei_to_iiif_annotations.py
                └── iiif/*-annotations.json  ← TEIから生成する派生物
                         │
                         ├── scripts/validate_iiif_annotations.py
                         │       └── 本文・Canvas・座標をTEIと再照合
                         │
                         └── viewer/index.html
                                 └── 外交的転写・正規化・並列画像表示
```

最重要原則は、**TEIを構造化本文の正本とし、IIIF Annotationを派生物として再生成可能にすること**である。画面やJSONを手作業で直すとTEIとの不一致が生じるため、修正は原則としてTEIまたは変換規則へ戻して行う。

## 3. 一つの半句を追跡する

例として`mt.bnf348.0004.b`を追う。

### 3.1 TEI本文

`data/tei/bnf-persan-348-f6-sample.xml`では、一つの`<l>`の中に非選択的校異を置く。

```xml
<l n="b" xml:id="mt.bnf348.0004.b" facs="#bnf348.f6.z004b">
  <app type="variant">
    <rdg wit="#wit-bnf348">وین دگر</rdg>
    <rdg wit="#wit-fsc28">وان ...</rdg>
  </app>
  را دایما آرام داد
</l>
```

- `xml:id`：半句の安定識別子。
- `@facs`：BnF画像上の`zone`への参照。
- `<app>`：同じ箇所に複数の証人読みがあること。
- `<rdg wit="...">`：各写本に基づく読み。
- `<lem>`を置かない理由：現段階では採用本文を選ばないため。

### 3.2 画像領域

`@facs="#bnf348.f6.z004b"`は同じTEI文書の`<zone>`を指す。`zone`の`ulx, uly, lrx, lry`は左上・右下座標である。親`surface/@corresp`がIIIF Canvasを指定する。

### 3.3 IIIF Annotation

`scripts/tei_to_iiif_annotations.py`は、証人に対応する外交的本文を取り出し、座標を`xywh=x,y,width,height`へ変換する。結果は`iiif/bnf-persan-348-f6-annotations.json`に入る。

### 3.4 閲覧画面

`viewer/index.html`はTEI、生成済みAnnotationPage、外部IIIF Manifestを読み、証人切替・並列表示・領域表示を行う。画面が研究上の正本なのではなく、TEIとIIIFを利用する提示層である。

## 4. 検証層を区別する

| 検証 | 主な問い | 成功しても保証しないこと |
|---|---|---|
| XML構文 | タグの開閉や属性引用符は正しいか | TEIとして妥当か、読みが正しいか |
| 公式TEI P5 RNG | TEI P5の一般文法に合うか | 本プロジェクトの編集方針に合うか |
| ODD由来RNG | 採用したTEIモジュール内か | 対句が必ず二半句か、座標が妥当か |
| Schematron | ID、二半句、証人参照、座標など独自規則に合うか | 写本の読みや領域が学術的に正しいか |
| TEI→IIIF変換 | TEIから決定的にAnnotationを作れるか | TEIの入力判断自体が正しいか |
| TEI–IIIF相互照合 | 派生JSONの本文・Canvas・座標がTEIと一致するか | 外部IIIFサービスが将来も利用可能か |
| 画面回帰検査 | 必要な表示機能がコードに存在するか | 全ブラウザで視覚的に完全か |
| 研究者画像照合 | 読みと領域が写本画像に合うか | 外部査読や批判校訂版としての妥当性 |

## 5. コードを読む順番

### 第1回：データモデル（30分）

1. `data/tei/bnf-persan-348-f6-sample.xml`で`mt.bnf348.0004`を探す。
2. 対句`<lg>`、半句`<l>`、異読`<app>/<rdg>`、`@facs`を確認する。
3. `bnf348.f6.z004b`と`fsc28.fs7342-15.z004b`を探す。
4. 「本文構造」「証人読み」「画像領域」が同じTEI内でどう接続されるか、自分の言葉で説明する。

### 第2回：規則（30分）

1. `schema/mantiq.odd`の`moduleRef`を見る。
2. `schema/mantiq.sch`の`couplet-structure`と`facsimile-alignment`を見る。
3. 公式TEI RNG、ODD由来RNG、Schematronの役割の違いを説明する。

### 第3回：変換（30分）

1. `scripts/tei_to_iiif_annotations.py`の`diplomatic_text()`を見る。
2. `build_annotation_pages()`で`zone`、`line`、`Canvas`が集められる順番を見る。
3. 座標が`xywh`へ変換される箇所を見る。
4. 出力JSONの一件をTEIの一半句と照合する。

### 第4回：検証（30分）

1. `scripts/validate.py`の三検証層を見る。
2. `scripts/validate_iiif_annotations.py`で期待値をTEIから再構築していることを確認する。
3. `scripts/verify_all.py`で全処理の実行順序を見る。
4. `outputs/project-verification-summary.json`で各処理の成否を見る。

### 第5回：安全な破壊テスト（20分）

次を実行する。

```powershell
python scripts/learning_negative_tests.py
```

このスクリプトは`work/`内の一時コピーだけを変更し、正本や公開ファイルは変更しない。次の三つを試す。

1. 最初の対句から第二半句を除く。
2. 半句の`@facs`を存在しないzoneへ向ける。
3. 生成後のIIIF Annotation本文だけを書き換える。

結果は`work/learning-negative-tests.json`へ保存される。すべての`detected`と`all_expected_failures_detected`が`true`であれば、想定した防御層が働いたことを意味する。

## 6. 研究者が答えられるようにする質問

1. なぜ刊本ではなく写本画像に基づく転写から始めたのか。
2. なぜPersan 348を「底本」や「最良写本」と呼ばないのか。
3. `<choice>`と`<app>`は何が違うのか。
4. `<unclear>`と`<gap>`は何が違うのか。
5. なぜ`<lem>`を選ばない校異を採用した箇所があるのか。
6. TEIとIIIFはどちらが本文の正本か。
7. ODDとSchematronを両方使う理由は何か。
8. 検証が全成功しても、なぜ写本の読みが正しいとは限らないのか。
9. AIが誤る可能性が最も高い工程はどこか。
10. 別の写本へ拡張するとき、何を再利用し、何を研究者が新たに判断するか。

## 7. 暗記しなくてよいもの

- Pythonの全構文。
- XPath式を一から書く方法。
- Relax NGファイルの自動生成部分。
- JSONの全キーの順序。
- Miradorの内部API。
- 78件のIDや座標値。

必要なのは、入力・正本・派生物・検証・研究判断の位置関係である。実装の細部はAIへ委任できるが、設計の意味と検証の限界は研究者本人が説明する。

## 8. レビュー完了の基準

次の四点を、コードを見ながら自分の言葉で説明できればよい。

1. 一つの半句がTEIからIIIF Annotationと閲覧画面へ届く経路。
2. 公式TEI、ODD、Schematron、相互照合の違い。
3. AIによる生成と研究者による承認の境界。
4. 意図的に壊した三例を、どの検証が検出したか。
