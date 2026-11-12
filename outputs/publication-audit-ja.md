# 公開監査報告

監査日：2026年11月12日
対象：*Manṭiq al-ṭayr* TEI–IIIF prototype 0.2.0
状態：技術検証済み。担当研究者の承認に基づき、v0.2.0として公開

## 1. 結論

リポジトリは、公開前に機械確認できる技術条件を満たす状態へ整備した。TEI・IIIF・校合・閲覧画面の総合検証、著者・引用情報、プロジェクト作成物のライセンス、第三者画像の出典と条件、再現手順を収録している。

担当研究者は2026年11月12日に公開を承認した。リポジトリ、GitHub Pages、`v0.2.0`タグ、GitHub Releaseを公開対象とする。Zenodo連携とDOI発行は、外部アカウント連携を要する次段階として切り分ける。

## 2. 公開対象

- Persan 348：30対句・60半句の外交的転写と画像領域。
- FSC-MS-28：冒頭9対句・18半句の独立転写と画像領域。
- 二写本の重複18半句の校合：16一致、1本文異同、1補修欠損。
- TEI ODD、Relax NG、Schematron、変換・検証コード。
- 3 Canvas・78 AnnotationのIIIF Presentation 3 AnnotationPage。
- 証人切替・並列比較・画像領域表示・Miradorを備えた閲覧画面。
- 設計判断、研究者確認記録、技術報告、再現手順、機械検証結果。

## 3. ライセンスと第三者資料

プロジェクト作成のTEI転写、IIIF Annotation、検証結果、文書はCC BY 4.0、コードはMIT Licenseとする。この許諾は外部機関の写本画像には及ばない。

### BnF / Gallica

- 画像ファイルはリポジトリへ複製せず、GallicaのIIIF URIを参照する。
- 指定出典表示：`Source gallica.bnf.fr / Bibliothèque nationale de France`。
- Gallicaの現行条件では、非商用再利用には出典表示が必要であり、商用再利用には別の条件がある。
- 公式条件：<https://gallica.bnf.fr/accueil/fr/html/conditions-dutilisation-de-gallica>

### Smithsonian National Museum of Asian Art

- FSC-MS-28画像はリポジトリへ複製せず、SmithsonianのIIIF URIを参照する。
- 公式資料ページは`Usage Conditions Apply`と表示する。
- 本試作は学術・教育目的の非商用デモとして位置付ける。商用利用や条件を超える利用には別途確認・許諾が必要となり得る。
- 公式資料：<https://asia.si.edu/explore-art-culture/collections/search/edanmdm:fsg_FSC-MS-28/>
- 利用条件：<https://www.si.edu/termsofuse>

本報告は法的助言ではなく、公式ページに表示された条件を公開物へ正確に伝えるための確認記録である。最終的な利用判断は研究者が行う。

## 4. 公開ツリーから除外されるもの

`.gitignore`により、`private/`、`work/`、`tmp/`、`output/`、ログ、キャッシュ、作業用画像を公開対象から除外している。追跡対象ファイルにはローカル絶対パス、秘密鍵、APIキー、パスワードを確認していない。

## 5. 学術的な表示上の制限

- 本成果は批判校訂版ではなく、小規模な二写本転写・校合試作である。
- Persan 348を最良写本または校訂底本として認定していない。
- 「研究者確認済み」はプロジェクト担当研究者による画像照合を意味し、外部査読を意味しない。
- FSC-MS-28の`دگر`は語として採用するが、`د`を字母単位で`unclear`とする。
- FSC-MS-28の0006aは他写本から補わず、補修紙による`gap`としている。
- 日本語訳対応、話者、物語階層、複数写本によるlemma選択は未実装である。

## 6. 公開判断と公開後確認

1. Git差分、個人情報、秘密情報、第三者画像ファイルの不在を機械・目視確認した。
2. バージョン番号を`0.2.0`とした。
3. 担当研究者がGitHub公開を明示的に承認した。
4. 公開後、GitHub ActionsとGitHub Pagesの正常終了を確認する。
5. 公開URLからREADME、Citation、IIIF AnnotationPageを取得できることを確認する。
6. DOIを付ける場合、GitHub Release確定後にZenodoで登録する。
