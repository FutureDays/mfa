'''
reads lines from hard drive manifest and outputs mods
'''
import os
import re
import sys
from bs4 import BeautifulSoup as bs

class dotdict(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

def make_indvline_dict(line):
    columns = ["filepath", "date", "title", "performers"]
    dct = dotdict({})
    row = line.split("\t")
    count = 0
    for column in columns:
        try:
            dct[column] = row[count].rstrip()
        except:
            dct[column] = ''
        count = count+1
    return dct

def grip_out_fname(dct):
	match = ''
	#match = re.search(r"\d{4}\w{4}.*\.MP3",dct.filepath)
	print "dct.filepath"
	print dct.filepath
	print " "
	match = re.search(r"\d{4}\w{2}.*MP3",dct.filepath)
	if not match:
		match = re.search(r"\d{4}\w{2}.*WAV",dct.filepath)
	if match:
		dct.outfname = match.group()
		dct.outfname, dct.ext = os.path.splitext(dct.outfname)
	else:
		print "something's up with this filename"
	return dct

def performers2list(dct):
    prf = dct.performers.replace('"','').split(" and ")
    dct.performers = prf
    return dct

def make_iso_dt(dct):
	if len(dct.date) == 3:
		dct.date = "20120" + dct.date
	elif len(dct.date) == 4:
		dct.date = "2012" + dct.date
	dt = dct.date[:4] + "-" + dct.date[4:6] + "-" + dct.date[6:8]
	dct.date = dt
	return dct

def make_soup_titles(dct, soup):
	soup.mods.append(soup.new_tag("titleInfo"))
	soup.titleInfo.append(soup.new_tag("title"))
	soup.title.string = dct.title
	return soup

def make_soup_names(perf, soup):
	anme = soup.new_tag("name")
	anme.append(soup.new_tag("namePart"))
	anme.namePart.string = perf
	anme.append(soup.new_tag("role"))
	anme.role.append(soup.new_tag("roleTerm", authority="marcrelator", type="text"))
	anme.roleTerm.string = "prf"
	return anme

def make_soup_dates(dct, soup):
	soup.mods.append(soup.new_tag("dateCreated"))
	soup.dateCreated.string = dct.date
	return soup

def make_mods(dct):
	#soup = bs(features='xml')
	foo = '''<mods
	xmlns="http://www.loc.gov/mods/v3"
	xmlns:mods="http://www.loc.gov/mods/v3"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:xlink="http://www.w3.org/1999/xlink">'''
	#soup.append(foo,"xml")
	soup = bs(foo,"xml")
	soup = make_soup_titles(dct,soup)
	for perf in dct.performers:
		anme = make_soup_names(perf,soup)
		soup.mods.append(anme)
	soup = make_soup_dates(dct, soup)
	#soup.append("</mods>")
	print soup.prettify()
	return soup

def make_out_xmlfile(dct):
	print "dct.outfname"
	print dct.outfname
	print "dct.ext"
	print dct.ext
	print dct.outfname + dct.ext
	print " "
	objPath = "/Volumes/feinstein_2014-2017_clone/2012"
	xmlpath = "/Volumes"
	if os.path.exists(objPath):
		for dirs, subdirs, files in os.walk(objPath):
			for f in files:
				if f == dct.outfname + dct.ext or f == os.path.basename(dct.outfname) + dct.ext:
					#dct.outxmlpath = os.path.join(dirs, dct.outfname + ".xml")
					dct.outxmlpath = os.path.join("/Volumes/thedata/developments/mfa/mtd/converter-xlsx2mods-outs",dct.outfname + ".xml")
	if not dct.outxmlpath:
		dct.outxmlpath = os.path.join("/Volumes/thedata/developments/mfa/mtd/converter-xlsx2mods-outs-leftovers",dct.outfname + ".xml")
	if os.path.exists(dct.outxmlpath):
		return dct, True
	else:
		return dct, False

def write_file(dct, mods):
	with open(dct.outxmlpath, "w") as f:
		f.write(str(mods))

def main():
    fname = "mfs-hard-drives1-mtd-2011-2012.txt"
    fullf = os.path.join("/Volumes/thedata/developments/mfa/mtd",fname)
    with open(fullf) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    for line in content:
		dct = make_indvline_dict(line)
		dct = grip_out_fname(dct)
		dct, xmlexists = make_out_xmlfile(dct)
		#if xmlexists == True:
			#continue
		dct = performers2list(dct)
		#dct = make_iso_dt(dct)
		dct.title = dct.date + " - " + dct.title
		mods = make_mods(dct)

		print dct.outxmlpath
		write_file(dct, mods)
		#foo = raw_input("eh")
main()
