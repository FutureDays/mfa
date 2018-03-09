#!/usr/bin/env python
'''
helps the metadata ~flow~
'''
import os
import re
import pdb
import json
from nltk.tag import pos_tag
import argparse
from dateutil.parser import *
import datetime
import subprocess
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
    try:
        thedate = parse(date)
        thedate = thedate.strftime("%Y-%m-%d")
    except:
        thedate = date
    return thedate

def export_ffmtd(thefile):
    '''
    extracts bwf metadata to dictionary
    '''
    #output = subprocess.Popen('ffprobe -show_streams -show_data -print_format xml "' + thefile.inFP + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out = output.communicate()
    out = subprocess.check_output('ffmpeg -hide_banner -i "' + thefile.inFP + '" -y -f ffmetadata mtd.txt', shell=True)
    return out

def import_ffmtd():
    '''
    imports ;FFMETADATA1 from mtd.txt
    '''
    with open("mtd.txt","r") as mtd:
        key = "title"
        foo = mtd.readlines()
        line = ''
        theline = ''
        for line in foo:
            if line.startswith(key):
                theline = line
                break
        return theline

def make_nameroles(title, rd):
    '''
    converts raw title string from ffmtd to nameroles dictionary
    '''
    title = title.strip()
    names = title.split("_")
    try:
        names = names[1].split("/")
    except:
        nameroles = {}
        return nameroles, False
    nameroles = dotdict({})
    nr = ["a","b","c","d","e","f","g","h","i","j","k","l"]
    count = 0
    instr = False
    for n in names:
        n = n.strip()
        nmbr = nr[count]
        count = count+1
        nameroles[nmbr] = dotdict({})
        if "Feinstein" in n or "MF" in n:
            nameroles[nmbr].name = "Michael Feinstein"
            role = n.replace("Feinstein", "").replace("MF", "").replace("Michael Feinstein", "").strip()
            if role:
                nameroles[nmbr].role = re.sub(r"[^a-zA-Z]", '', role)
            else:
                nameroles[nmbr].role = "prf"
        elif n == "Rosemary Clooney" or "Clooney" in n:
            nameroles[nmbr].name = "Rosemary Clooney"
            nameroles[nmbr].role = 'prf'
        else:
            tagged_sent = pos_tag(n.split())
            propernouns = [word for word, pos in tagged_sent if pos == 'NNP']
            anme = ''
            for p in propernouns:
                anme = anme + p + ' '
            #anme = propernouns[0] + ' ' + propernouns[1]
            #print(anme)
            anme = re.sub(r"[^a-zA-Z\d\s]", '', anme)
            nameroles[nmbr].name = anme.strip()
            role = n.replace(anme.strip(), "")
            if not nameroles[nmbr].name:
                nameroles[nmbr].name = n.strip()
            if role:
                nameroles[nmbr].role = re.sub(r"[^a-zA-Z]", '', role)
            else:
                nameroles[nmbr].role = "prf"
            elems = re.sub(r"[^a-zA-Z]", '', role).split()
            for e in elems:
                if e in nameroles[nmbr].role:
                    nameroles[nmbr].role = 'prf'
        ###### before this is real you gotta make sure nothing is in these files
        if not nameroles[nmbr].name:
            return {}, False
        if nameroles[nmbr].role == "w":
            nameroles[nmbr].role = "prf"
        elif "piano" in nameroles[nmbr].role:
            nameroles[nmbr].role = "mus"
            instr = "piano"
        elif "solo" in nameroles[nmbr].role or "Solo" in nameroles[nmbr].role:
            nameroles[nmbr].role = "prf"
            instr = "piano"

    return nameroles, instr

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
    offset = 2
    row = 2
    for dirs, subdirs, files in os.walk(args.dir):
        for f in files:
            filefp = os.path.join(dirs, f)
            print(filefp)
            thefile = make_thefile(filefp, args)
            output = export_ffmtd(thefile)
            ffout = output
            title = import_ffmtd()
            if title and not title == "0":
                nrs, piano = make_nameroles(title, rd)
            elif title == "0":
                title = "Untitled"
                nrs = {}
            else:
                title = "Untitled"
                nrs = {}
            #make_names(nrs)
            rd.nameroles = json.dumps(nrs)
            if piano:
                rd.note = piano
            elements = thefile.fname.split('_')
            rd.placeTerm = elements[2].replace('-'," ")
            rd.dateIssued = daterizer(elements[1])
            rd.language = 'eng'
            rd.title = rd.dateIssued + " - " + rd.placeTerm
            rd.identifier = elements[0]
            rd.filename = thefile.fname
            g.insert_row(rl, rd, row, sh)
            row = row + 1
            #foo = raw_input("eh")




if __name__ == "__main__":
    main()
