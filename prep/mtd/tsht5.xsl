<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes"/>
	<xsl:strip-space elements="*"/>
	<xsl:template match="node() | @*">
		<xsl:copy>
 			<xsl:apply-templates select="node() | @*" />
		</xsl:copy>
	</xsl:template>
	<xsl:template match=
    "*[not(@*|*|comment()|processing-instruction()) 
     and normalize-space()=''
      ]"/>
	<xsl:template match="ROW">
		<mods xmlns="http://www.loc.gov/mods/v3" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">
		<xsl:apply-templates select="Title"/>
		<xsl:apply-templates select="Arranger"/>
		<xsl:apply-templates select="Adapter"/>
		<xsl:apply-templates select="Composer"/>
		<xsl:apply-templates select="Editor"/>
		<xsl:apply-templates select="Lyricist"/>
		<xsl:apply-templates select="Transcriber"/>
		<xsl:apply-templates select="Reconstructor"/>
		<xsl:apply-templates select="Publisher"/>
		<xsl:apply-templates select="Score_Number"/>
		<xsl:apply-templates select="Parts_Number"/>
		<xsl:apply-templates select="Instrumentation"/>
		<xsl:apply-templates select="Kind"/>
		<xsl:apply-templates select="Score_Folder_Contents"/>
		<xsl:apply-templates select="Ensemble"/>
		<xsl:apply-templates select="Collection"/>
		<xsl:apply-templates select="Where"/>
		<language>
			<languageTerm authority="iso639-2b" type="code">eng</languageTerm>
		</language>
		<accessCondition/>
		</mods>
	</xsl:template>
	<xsl:template match="Title">
	<titleInfo>
			<title><xsl:value-of select="/ROW/Title"/></title>
			<subTitle/>
		</titleInfo>
	</xsl:template>
	<xsl:template match="Arranger">
		<name>
			<namePart><xsl:value-of select="/ROW/Arranger"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">arr</roleTerm>	
			</role>
		</name>
	</xsl:template>
	<xsl:template match="Adapter">
			<name>
			<namePart><xsl:value-of select="/ROW/Adapter"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">adp</roleTerm>	
			</role>
		</name>
	</xsl:template>	
	<xsl:template match="Composer">	
		<name>
			<namePart><xsl:value-of select="/ROW/Composer"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">cmp</roleTerm>	
			</role>
		</name>
	</xsl:template>	
	<xsl:template match="Editor">	
		<name>
			<namePart><xsl:value-of select="/ROW/Editor"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">edt</roleTerm>	
			</role>
		</name>
	</xsl:template>	
	<xsl:template match="Lyricist">	
		<name>
			<namePart><xsl:value-of select="/ROW/Lyricist"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">lyr</roleTerm>	
			</role>
		</name>
	</xsl:template>	
	<xsl:template match="Reconstructor">	
		<note type="reconstructor"><xsl:value-of select="/ROW/Reconstructor"/></note>
	</xsl:template>
	<xsl:template match="Publisher">
		<originInfo>
			<dateCreated/>
			<publisher><xsl:value-of select="/ROW/Publisher"/></publisher>
		</originInfo>
	</xsl:template>
	<xsl:template match="Score_Number">
		<identifier type="sn"><xsl:value-of select="/ROW/Score_Number"/></identifier>
	</xsl:template>
	<xsl:template match="Parts_Number">
		<identifier type="pn"><xsl:value-of select="/ROW/Parts_Number"/></identifier>
	</xsl:template>
	<xsl:template match="Instrumentation">
		<note type="instrumentation"><xsl:value-of select="/ROW/Instrumentation"/></note>
	</xsl:template>
	<xsl:template match="Kind">
		<genre><xsl:value-of select="/ROW/Kind"/></genre>
	</xsl:template>
	<xsl:template match="Score_Folder_Contents">
		<tableOfContents type="scoreFolderContents"><xsl:value-of select="/ROW/Score_Folder_Contents"/></tableOfContents>
	</xsl:template>
	<xsl:template match="Ensemble">
		<note type="ensemble"><xsl:value-of select="/ROW/Ensemble"/></note>
	</xsl:template>
	<xsl:template match="Collection">
		<note type="collection"><xsl:value-of select="/ROW/Collection"/></note>
	</xsl:template>
	<xsl:template match="Where">
		<location>
			<physicalLocation><xsl:value-of select="ROW/Where"/></physicalLocation>
		</location>
	</xsl:template>
		
</xsl:stylesheet>