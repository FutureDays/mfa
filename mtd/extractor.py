'''
extracts individual glendower basement music records from fmp dump
outputs xmls as:
<ROW>
etc
</ROW>

named as TBD
uniqueID = TBD or RECORDID
splits values on commas for name fields
then they're ready to be processed by xslt
'''
from bs4 import BeautifulSoup
import os

def replace_tags(row,replacer):
	sp = BeautifulSoup(row.prettify(),'lxml-xml')
	for k,v in replacer.iteritems():
		if k == 'Adapter':
			sp.Adapter.extract()
		elif k == "Arranger":
			print v
			sp.Arranger.extract()
		elif k == "Composer":
			sp.Composer.extract()
		elif k == "Editor":
			sp.Editor.extract()
		elif k == "Lyricist":
			sp.Lyricist.extract()
		elif k == "Transcriber":
			sp.Transcriber.extract()
		elif k == "Reconstructor":
			sp.Reconstructor.extract()
		#newlines = sp.k.replace_with(v)
		for name in v:
			nt = sp.new_tag(k)
			nt.string=name
			sp.Chorus.insert_before(nt)
	return sp
	
def split_names_on_comma(row):
	nametags = ["Adapter","Arranger","Composer","Editor","Lyricist","Transcriber","Reconstructor"]
	replacer = {}
	for tag in row.contents:
		#print row.contents[count]
		if tag.name in nametags:
			try:
				if "," in tag.string:
					value = tag.string
					newtag = []
					for v in value.split(", "):
						#newtag = '<' + tag.name + '>' + v + '</' + tag.name + '>' + newtag
						newtag.append(v)
					replacer[tag.name]=newtag
			except:
				pass
	newrow = replace_tags(row,replacer)
	return newrow

def export_file(row,recordid):
	fname = recordid
	fpath = os.path.join("S:/avlab/mfa/mtd/soup_outs/", fname + ".xml")
	f = open(fpath, "w")
	f.write(row.prettify().encode("UTF-8"))
	f.close()

def main():
	rawxml = open("S:/avlab/mfa/mtd/srce2-simp1.xml","r")
	soup = BeautifulSoup(rawxml,"lxml-xml")
	everyrow = soup.find_all("ROW")
	for row in everyrow:
		recordid = row['RECORDID']
		row = split_names_on_comma(row)
		#print row.prettify()
		export_file(row,recordid)
main()