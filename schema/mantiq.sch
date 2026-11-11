<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron"
        xmlns:tei="http://www.tei-c.org/ns/1.0"
        queryBinding="xslt">
  <title>Manṭiq al-ṭayr project constraints</title>
  <ns prefix="tei" uri="http://www.tei-c.org/ns/1.0"/>

  <pattern id="couplet-structure">
    <rule context="tei:lg[@type='couplet']">
      <assert test="string-length(@n) = 4 and translate(@n, '0123456789', '') = ''">対句の@nは4桁の数字であること。</assert>
      <assert test="count(tei:l) = 2">対句はちょうど2つの半句を持つこと。</assert>
      <assert test="tei:l[1]/@n = 'a' and tei:l[2]/@n = 'b'">半句の@nは順にa, bであること。</assert>
      <assert test="starts-with(@xml:id, 'mt.')">xml:idはmt.で始まること。</assert>
    </rule>
  </pattern>

  <pattern id="hemistich-identity">
    <rule context="tei:lg[@type='couplet']/tei:l">
      <assert test="parent::tei:lg[@type='couplet']">半句lは@type='couplet'のlgの直下にあること。</assert>
      <assert test="@xml:id = concat(parent::tei:lg/@xml:id, '.', @n)">半句IDは対句IDとa/bから一意に作ること。</assert>
      <assert test="normalize-space(.) != ''">半句本文は空でないこと。</assert>
    </rule>
  </pattern>

  <pattern id="research-provenance">
    <rule context="tei:div[@type='section']">
      <assert test="@source">本文セクションには@sourceを付けること。</assert>
    </rule>
    <rule context="tei:app">
      <assert test="tei:lem and tei:rdg">校異にはlemと少なくとも1つのrdgを含めること。</assert>
      <assert test="count((tei:lem | tei:rdg)[not(@wit)]) = 0">すべてのlem/rdgに写本根拠@witを付けること。</assert>
    </rule>
  </pattern>

  <pattern id="normalization-choice">
    <rule context="tei:choice[tei:orig or tei:reg]">
      <assert test="count(tei:orig) = 1 and count(tei:reg) = 1">正規化用choiceはorigとregを1つずつ持つこと。</assert>
      <assert test="count(*) = 2">正規化用choiceにはorigとreg以外の子要素を混在させないこと。</assert>
      <assert test="*[1][self::tei:orig] and *[2][self::tei:reg]">正規化用choiceではorigを先、regを後に置くこと。</assert>
      <assert test="tei:reg/@resp">正規化形regには責任主体を示す@respを付けること。</assert>
    </rule>
    <rule context="tei:reg">
      <assert test="parent::tei:choice/tei:orig">regは対応するorigを持つchoice内に置くこと。</assert>
      <assert test="normalize-space(.) != ''">regの正規化形は空でないこと。</assert>
    </rule>
    <rule context="tei:text">
      <assert test="not(contains(., 'ك')) and not(contains(., 'ي')) and not(contains(., 'ى'))">ペルシア語本文ではアラビア語用ك・ي・ىを使わず、ک・یへUnicode字形を統一すること。</assert>
    </rule>
  </pattern>

  <pattern id="facsimile-alignment">
    <rule context="tei:surface">
      <assert test="starts-with(@corresp, 'http://') or starts-with(@corresp, 'https://')">各surfaceには対応するIIIF CanvasのHTTP(S) URIを@correspで付けること。</assert>
      <assert test="count(tei:graphic) = 1">各surfaceは画像取得元を示すgraphicを1つ持つこと。</assert>
    </rule>
    <rule context="tei:lg[@type='couplet']/tei:l">
      <assert test="starts-with(@facs, '#')">各半句には#で始まるzone参照@facsを付けること。</assert>
      <assert test="id(substring-after(@facs, '#'))[self::tei:zone]">各半句の@facsは実在するTEI zoneを参照すること。</assert>
    </rule>
    <rule context="tei:surface/tei:zone">
      <assert test="parent::tei:surface/@corresp">各zoneの親surfaceにはIIIF Canvas参照@correspがあること。</assert>
      <assert test="number(@ulx) &lt; number(@lrx) and number(@uly) &lt; number(@lry)">zoneは正の幅と高さを持つこと。</assert>
      <assert test="number(@ulx) &gt;= number(parent::tei:surface/@ulx) and number(@uly) &gt;= number(parent::tei:surface/@uly)">zoneの左上はsurfaceの範囲内にあること。</assert>
      <assert test="number(@lrx) &lt;= number(parent::tei:surface/@lrx) and number(@lry) &lt;= number(parent::tei:surface/@lry)">zoneの右下はsurfaceの範囲内にあること。</assert>
    </rule>
  </pattern>
</schema>
