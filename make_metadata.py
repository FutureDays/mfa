#!/usr/bin/env python
'''
helps the metadata ~flow~
'''
import os
import pdb
import argparse
from dateutil.parser import *
import datetime
import ghandler as g

class dotdict(dict):
    '''
    dot["notation"] == dot.notation for dictionary attributes
    '''
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def init_args_cli():
    '''
    initialize arguments from the cli
    '''
    parser = argparse.ArgumentParser(description="makes the metadata ~flow~")
    parser.add_argument('-dir',dest='dir', help="the directory you want to work through")
    args = parser.parse_args()
    return args

def config(args):
    '''
    configuration info, where to find things, etc
    '''
    args.dir = "/Volumes/My Passport/Micheal Feinstein Audio Files"
    return args

def make_thefile(fileFP, args):
    '''
    returns a dictionary of file attributes/ paths
    '''
    thefile = dotdict({})
    thefile.inFP = fileFP
    thefile.fname, thefile.ext = os.path.splitext(os.path.basename(fileFP))
    thefile.dir = os.path.dirname(thefile.inFP)
    return thefile

def daterizer(date):
    '''
    parses input file for placeTerm
    '''
    foo = parse(date)
    foo = foo.strftime("%Y-%m-%d")
    return foo

def main():
    '''
    do the things:
    extract bwf metadata
    write xml to file
    '''
    args = dotdict({})
    args = config(args)
    gc = g.authorize()
    sh = gc.open("mfa_descriptiveMetadata").sheet1
    rl = sh.row_values(1)
    rd = dotdict(g.make_rowdict(sh))
    row = 2
    for dirs, subdirs, files in os.walk(args.dir):
        for f in files:
            filefp = os.path.join(dirs, f)
            print(filefp)
            thefile = make_thefile(filefp, args)

            elements = thefile.fname.split('_')
            rd.placeTerm = elements[2].replace('-'," ")
            rd.dateIssued = daterizer(elements[1])
            rd.language = 'eng'
            rd.title = rd.dateIssued + " - " + rd.placeTerm
            rd.identifier = elements[0]
            rd.filename = thefile.fname
            g.insert_row(rl, rd, row, sh)
            row = row + 1
            foo = raw_input("eh")




if __name__ == "__main__":
    main()
