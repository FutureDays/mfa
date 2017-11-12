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
		<name>
			<namePart><xsl:value-of select="ROW/Arranger"/></namePart>
			<role>
				<roleTerm authority="marcrelator" type="text">arr</roleTerm>	
			</role>
		</name>	
		<!--</xsl:copy>-->
	<!--</xsl:for-each>-->
	</xsl:template>
	<!--<xsl:template match="ROW/node()"/>-->
</xsl:stylesheet>
