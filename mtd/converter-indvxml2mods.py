'''
loops through soup_outs and runs an xslt on every xml file there
'''

import os
import subprocess

soups = "S:/avlab/mfa/mtd/soup_outs"
xslt = "S:/avlab/mfa/mtd/gbmFMROW_to_MODS.xsl"
xsltproc = "C:/Users/specpa7/Desktop/msxsl.exe"
outs = "S:/avlab/mfa/mtd/converter-outs"
for _, _, files in os.walk(soups):
    for f in files:
        outxml = os.path.join(outs, f)
        fullf = os.path.join(soups, f)
        subprocess.call([xsltproc, fullf, xslt, "-o", outxml])
