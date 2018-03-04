<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes"/>
	
	<!--<xsl:template match="node() | @*">-->
		<!--<xsl:copy>-->
 			<!--<xsl:apply-templates select="node() | @*" />-->
		<!--</xsl:copy>-->
	<!--</xsl:template>-->
	<xsl:template match="/">
	<!--<xsl:for-each select="FMPDSORESULT/ROW">-->
		<!--<xsl:copy>-->
		<mods xmlns="http://www.loc.gov/mods/v3" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">
		<titleInfo>
			<title><xsl:value-of select="ROW/Title"/></title>
			<subTitle/>
		</titleInfo>
		<name>
			<namePart><xsl:value-of select="ROW/Arranger"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">arr</roleTerm>	
			</role>
		</name>
		<name>
			<namePart><xsl:value-of select="ROW/Adapter"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">adp</roleTerm>	
			</role>
		</name>
		<name>
			<namePart><xsl:value-of select="ROW/Composer"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">cmp</roleTerm>	
			</role>
		</name>
		<name>
			<namePart><xsl:value-of select="ROW/Editor"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">edt</roleTerm>	
			</role>
		</name>
		<name>
			<namePart><xsl:value-of select="ROW/Lyricist"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">lyr</roleTerm>	
			</role>
		</name>
		<note type="reconstructor"><xsl:value-of select="ROW/Reconstructor"/></note>
		<originInfo>
			<dateCreated/>
			<publisher><xsl:value-of select="ROW/Publisher"/></publisher>
		</originInfo>
		<identifier type="sn"><xsl:value-of select="ROW/Score_Number"/></identifier>
		<identifier type="pn"><xsl:value-of select="ROW/Parts_Number"/></identifier>
		<note type="instrumentation"><xsl:value-of select="ROW/Instrumentation"/></note>
		<genre><xsl:value-of select="ROW/Kind"/></genre>
		<tableOfContents type="scoreFolderContents"><xsl:value-of select="Score_Folder_Contents"/></tableOfContents>
		<note type="ensemble"><xsl:value-of select="ROW/Ensemble"/></note>
		<note type="collection"><xsl:value-of select="ROW/Collection"/></note>
		<language>
			<languageTerm authority="iso639-2b" type="code">eng</languageTerm>
		</language>
		<location>
			<physicalLocation><xsl:value-of select="ROW/Where"/></physicalLocation>
		</location>
		<accessCondition/>
		<!--</xsl:copy>-->
	<!--</xsl:for-each>-->
	</mods>
	</xsl:template>
	<!--<xsl:template match="ROW/node()"/>-->
</xsl:stylesheet>
