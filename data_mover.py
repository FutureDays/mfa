#!/usr/bin/env python

'''
data_mover.py

moves data on disc
moves data to / from google sheets
'''

import os
import re
import wave
import time
import shutil
import argparse
import contextlib
import ghandler as gh
import gspread
import subprocess

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class dotdict(dict):
    '''
    dot["notation"] == dot.notation for dictionary attributes
    '''
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def hash_file(filepath):
    '''
    uses shasum to create SHA1 hash of file
    '''
    output = subprocess.check_output("shasum '" + filepath + "'", shell=True)
    match = ''
    #search for 40 consecutive word characters in string, convert byte output from shasum in CLI to utf-8 string
    match = re.search(r'\w{40}', output.decode("utf-8"))
    if match:
        #convert match object to string
        thehash= match.group()
        return thehash
    else:
        return "hash error"

def get_wav_duration(filepath):
    '''
    returns wave file duration hh:mm:ss
    '''
    with contextlib.closing(wave.open(filepath,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        duration = time.strftime('%H:%M:%S', time.gmtime(duration))
        return(duration)

def get_uid_from_file(filepath):
    '''
    extracts 5000x number from full path
    '''
    match = ''
    match = re.search(r'\d{14}', filepath)
    if match:
        uid = match.group()
        return uid
    else:
        return "uid extraction error"

def walk(path, args):
    '''
    walks a directory
    '''
    for dirs, subdirs, files in os.walk(path):
        for f in files[(int(args.start) - 6):]:
                print(f)
                gc = gh.authorize()
                spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
                worksheet = spreadsheet.worksheet("catalog")
                fullpath = os.path.join(dirs, f)
                uid = get_uid_from_file(fullpath)
                sheets_uid_match = gh.find_cell(uid, worksheet)
                row = str(sheets_uid_match.row)
                cell_is_empty = gh.cell_is_empty("N"+row,worksheet)
                if cell_is_empty:
                    #get duration and update catalog
                    print("getting duration...")
                    duration = get_wav_duration(fullpath)
                    gh.update_cell_value("K" + row, str(duration), worksheet)
                    #get hash and update catalog
                    print("hashing file...")
                    thehash = hash_file(fullpath)
                    gh.update_cell_value("N" + row, thehash, worksheet)
                time.sleep(4.0)

def cleaner(path, args):
    '''
    cleans and normalizes filepaths
    originally used to get rid of 'Unknown' in filenames e.g. 50000000002053_Dec-31-2009_'Unknown' - New Years Eve.wav
    '''
    for dirs, subdirs, files in os.walk(path):
        for f in files:
            #move XML files
            '''if f.endswith(".xml"):
                print(f)
                lastdirs = dirs.split("/")
                dest = "/Volumes/NAS_Public/hdd_uploads/feinstein_2014-2017_clone/forIslandora/" + lastdirs[-2] + "/" + lastdirs[-1]
                if not os.path.exists(dest):
                    os.makedirs(dest)
                print(dest)
                #input("heya")
                shutil.move(os.path.join(dirs,f), dest)
                #input("heya")'''
            #delete hidden files
            '''if f.startswith("."):
                print(f)
                #input("heya")
                os.remove(os.path.join(dirs,f))'''
            #_fullpath = os.path.join(dirs, f)
            lastdirs = dirs.split("/")
            lastdir = lastdirs[-2] + "/" + lastdirs[-1]
            #print(lastdir)
            print(f)
            '''if "'" in s:
                fullpath = os.path.join(dirs, s.replace("'", ""))
                print(fullpath)
                shutil.move(_fullpath, fullpath)
                #input("heya")'''

def moveDropboxToTraffic(args):
    '''
    checks if file is done copying - see if Dropbox is syncing currently?
    verify file not on NAS via catalog hash
    move file in tree to /NAS_Public/traffic
    '''
    if not os.path.exists(args.traffic):
        print("here2")
        print("mount the NAS before continuing!")
        exit()
    print(args.Dropbox)
    for dirs, subdirs, files in os.walk(args.Dropbox):
        print("here4")
        for f in files:
            if not "." in f:
                continue
            elif not ".tmp" in f and not f.startswith("."):
                fullpath = os.path.join(dirs,f)
                with cd(args.Dropbox):
                    output = subprocess.check_output('dropbox filestatus "' + f + '"', shell=True)
                    output = output.communicate()
                    output = output.decode("utf-8")
                #output = "/root/Dropbox/MF archival audio/20170225_PalmDesertAct2_T585.mp3: up to date"
                outList = output.split(":")
                status = outList[1].lstrip()
                if status == "up to date":
                    print("copying" + f)
                    subprocess.check_output('rsync -av --progress "' + fullpath + '" ' + args.traffic)
                else:
                    print("still copying " + outList[0])
    '''with cd(args.Dropbox):
        Dropbox = '/root/Dropbox'
        traffic = '/mnt/nas/traffic'
        filestatus = {}

        outList = output.split("\n")
        for pair in outList:
            filestatus[pair.split(":")[0].replace(":","")] = pair.split(":")[-1].lstrip()
        for fname, status in filestatus:
            if fname.endswith(".mp3") or fname.endswith(".zip") or fname.endswith("wav"):
                if status == 'up to date':'''




def init():
    '''
    initialize vars
    '''
    parser = argparse.ArgumentParser(description="makes the metadata ~flow~")
    parser.add_argument('-start',dest='start', help="the start UID (minus leading 500x) you want to hash")
    parser.add_argument('--moveDropboxToTraffic', dest='mdtt', action='store_true', help="moves file from Dropbox folder to traffic on NAS")
    args = parser.parse_args()
    return args

def main():
    '''
    do the thing
    '''
    args = init()
    args.Dropbox = "/root/Dropbox/MF archival audio"
    args.traffic = "/mnt/nas/traffic"
    print(args)
    if args.mdtt is True:
        print("here")
        moveDropboxToTraffic(args)
        exit()
    path = "/Volumes/My Passport/Micheal Feinstein Audio Files"
    cleanpath = "/Volumes/NAS_Public/hdd_uploads/feinstein_2014-2017_clone/compounded-objects"
    #cleaner(cleanpath, args)
    #walk(path, args)

if __name__ == '__main__':
    main()
