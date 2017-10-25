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
    columns = ["filepath", "date", "performers"]
    dct = dotdict({})
    row = line.split("\t")
    count = 0
    for column in columns:
        try:
            dct[column] = row[count]
        except:
            dct[column] = ''
        count = count+1
    return dct

def grip_out_fname(dct):
    macth = ''
    match = re.search(r"\d{4}\w{4}.*.MP3",dct.filepath)
    if match:
        dct.outfname = match.group()
    else:
        print "something's up with this filename"
    return dct

def performers2list(dct):
    prf = dct.performers.replace('"','').split(" and ")
    dct.performers = prf
    return dct

def make_iso_dt(dct):
	dt = dct.date[:4] + "-" + dct.date[4:6] + "-" + dct.date[6:8]
	dct.date = dt
	return dct

def make_soup_titles(dct, soup):
	soup.mods.append(soup.new_tag("titleInfo"))
	soup.titleInfo.append(soup.new_tag("title"))
	soup.title.string = dct.outfname
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
	print dct.outfname
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

def write_file(dct, mods, outs):
	fullout = os.path.join(outs, dct.outfname + ".xml")
	with open(fullout, "w") as f:
		f.write(str(mods))

def main():
    fname = "mfs-hard-drives1-mtd.txt"
    fullf = os.path.join("S:/avlab/mfa/mtd",fname)
    outs = "S:/avlab/mfa/mtd/converter-xlsx2mods-outs"
    with open(fullf) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    for line in content:
		dct = make_indvline_dict(line)
		dct = grip_out_fname(dct)
		dct = performers2list(dct)
		dct = make_iso_dt(dct)
		mods = make_mods(dct)
		write_file(dct, mods, outs)
		foo = raw_input("eh")
main()
