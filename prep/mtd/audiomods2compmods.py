'''
converts indv audio xml mods to compound obj mods
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

def make_soup(obj):
	with open(obj) as rawobj:
		soup = bs(rawobj,'lxml-xml')
		return soup

def main():
	hdd = "/Volumes/feinstein_2014-2017_clone/"
	year = "2012"
	for dirs, subdirs, files in os.walk(os.path.join(hdd, year)):
		for f in files:
			if f.endswith(".xml"):
				fullf = os.path.join(dirs,f)
				soup = make_soup(fullf)
				print soup.prettify()
				foo = raw_input("eh")

main()
