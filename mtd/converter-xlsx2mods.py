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
        print dct.outfname
    else:
        print "something's up with this filename"
    return dct

def performers2list(dct):
    prf = dct.performers.replace('"','').split(" and ")
    dct.performers = prf
    return dct

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
        print dct.performers
        foo = raw_input("eh")
main()
