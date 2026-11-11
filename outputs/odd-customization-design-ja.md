# Persan 348 TEI ODD設計・コードレビュー教材

更新日：2026年11月10日
ODD：`schema/mantiq.odd`
生成スキーマ：`schema/mantiq.rng`

## 1. ODDとは何か

ODD（One Document Does-it-all）は、TEIのどの部分をプロジェクトで使用するかを、TEI文書として記述する仕組みである。一つのODDから、Relax NGなどのスキーマと、人間向けの記述方針を生成できる。

公式説明：

- <https://tei-c.org/guidelines/customization/getting-started-with-p5-odds/>
- <https://tei-c.org/release/doc/tei-p5-doc/en/html/TD.html>

## 2. 本プロジェクトの選択

`schemaSpec`では次のモジュールを選択した。

| モジュール | 本プロジェクトでの役割 |
|---|---|
| `tei` | TEI共通属性と基盤 |
| `core` | `p`、`lg`、`l`、`choice`、`orig`、`reg`など |
| `header` | 出典、責任表示、編集方針、改訂履歴 |
| `textstructure` | `TEI`、`text`、`body`、`div` |
| `msdescription` | `msDesc`、支持体、書体、年代、写本識別 |
| `namesdates` | 人名・地名・所蔵地 |
| `transcr` | `facsimile`、`surface`、`zone` |
| `linking` | `surface/@corresp`によるIIIF Canvas参照と将来の本文・翻訳対応 |
| `textcrit` | 将来の`app`、`lem`、`rdg`、写本一覧 |

初版では要素を一つずつ削るのではなく、必要なモジュールを選ぶ方式を採用した。現在の18対句だけに過剰適合させず、20〜30対句への拡張と校異実装に耐える安定した出発点にするためである。要素単位の縮小は、実データ拡張後に使用実績を確認して行う。

## 3. 三つの検証層

### 公式TEI All

`tei_all.rng`は、文書がTEI P5全体の文法に適合するかを確認する。ここで失敗すれば、基本的なTEIの使用方法に問題がある。

### ODD生成スキーマ

`mantiq.rng`は、本プロジェクトが選択したモジュールの範囲内かを確認する。TEIでは使えるが、このプロジェクトでは採用していないモジュールを不用意に導入することを防ぐ。

### Schematron

`mantiq.sch`は、Relax NGだけでは表しにくいプロジェクト固有規則を検査する。たとえば、対句に半句が二つあること、半句IDが親の対句IDと対応すること、画像座標がsurfaceの範囲内にあることを確認する。

## 4. 再生成の流れ

```text
schema/mantiq.odd
  ↓ TEI Stylesheets odd2odd.xsl
展開済みODD
  ↓ TEI Stylesheets odd2relax.xsl
schema/mantiq.rng
  ↓ Jing
Persan 348 TEI試料を検証
```

`scripts/build_odd_schema.py`はTEI P5 4.12.0、TEI Stylesheets 7.61.0、StylesheetsのコミットID、取得ファイルのSHA-256を固定している。生成結果は`outputs/odd-build-report.json`に記録する。

## 5. コードレビューの順番

1. `schema/mantiq.odd`の`schemaSpec`を探す。
2. `moduleRef`の一覧が研究目的と一致するか確認する。
3. `scripts/build_odd_schema.py`でTEIとStylesheetsの版が固定されているか確認する。
4. `outputs/odd-build-report.json`で`odd_valid`と`sample_valid_against_generated_schema`が`true`か確認する。
5. `outputs/odd-negative-test-report.json`で、公式TEI Allが受理する`figure`を専用ODDが拒否しているか確認する。
6. `scripts/validate.py`で公式スキーマ、専用スキーマ、Schematronが別々に検査されているか確認する。

## 6. 研究者が承認した事項

2026年11月10日、研究者は次の二点を承認した。

1. 校異データをまだ投入していなくても、近接する拡張として`textcrit`モジュールをODDに含める。
2. 現段階ではモジュール単位のODDとし、20〜30対句への拡張後に要素単位でさらに縮小する。

この判断により、現在の18対句だけに過剰適合させず、次段階の校異実装に必要な語彙を確保しながら、実際の使用実績に基づいてスキーマを絞り込める。

## 7. 面接での説明例

> 汎用的なTEI Allだけに依存せず、研究目的に必要なモジュールをODDで明示し、専用Relax NGを再生成できるようにしました。公式スキーマはTEI全体への適合、ODD生成スキーマはプロジェクト語彙への適合、Schematronは対句構造や画像参照などの固有規則を担当します。これにより、規格適合と研究上のデータ方針を分けて説明・検証できます。
