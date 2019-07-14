#!/usr/bin/env python

'''
data_mover.py

moves data on disc
moves data to / from google sheets
'''

import os
import re
import copy
import wave
import time
import pprint
import shutil
import argparse
from datetime import datetime
import contextlib
import google_handler as gh
import make_filedata as mfd
import make_metadata as mtd
import make_rowObject
import gspread
import subprocess
from mutagen.mp3 import MP3
from pprint import pprint
from sys import platform

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

def get_file_duration(filepath):
    '''
    returns wave file duration hh:mm:ss
    '''
    if filepath.endswith("wav") or filepath.endswith("WAV"):
        with contextlib.closing(wave.open(filepath,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            duration = time.strftime('%H:%M:%S', time.gmtime(duration))
            return(duration)
    elif filepath.endswith("mp3") or filepath.endswith(".MP3"):
        audio = MP3(filepath)
        duration = audio.info.length
        duration = time.strftime('%H:%M:%S', time.gmtime(duration))
        return duration

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

def make_and_send_hash(path, args):
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
                uid = mfd.get_uid_from_file(fullpath)
                sheets_uid_match = gh.find_cell(uid, worksheet)
                row = str(sheets_uid_match.row)
                cell_is_empty = gh.cell_is_empty("N"+row,worksheet)
                if cell_is_empty:
                    #get duration and update catalog
                    print("getting duration...")
                    duration = get_file_duration(fullpath)
                    gh.update_cell_value("K" + row, str(duration), worksheet)
                    #get hash and update catalog
                    print("hashing file...")
                    thehash = mfd.hash_file(fullpath)
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
        print("mount the NAS before continuing!")
        exit()
    print(args.Dropbox)
    for dirs, subdirs, files in os.walk(args.Dropbox):
        for f in files:
            if not "." in f:
                continue
            elif not ".tmp" in f and not f.startswith("."):
                print("processing file " + f)
                fullpath = os.path.join(dirs,f)
                with cd(args.Dropbox):
                    output = subprocess.check_output('dropbox filestatus "' + f + '"', shell=True)
                    output = output.decode("utf-8")
                    print(output)
                #output = "/root/Dropbox/MF archival audio/20170225_PalmDesertAct2_T585.mp3: up to date"
                outList = output.split(":")
                status = outList[1].lstrip()
                print(status)
                if "up to date" in status:
                    print("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
                    args = gh.get_worksheet(args)
                    print("checking if file is cataloged in md.inventory_directory()")
                    file_is_cataloged, header_map = mtd.is_file_cataloged(os.path.join(args.path,file), args)
                    pprint(file_is_cataloged)
                    if not file_is_cataloged:
                        print("copying" + f)
                        subprocess.check_output('rsync -av --progress "' + fullpath + '" ' + args.traffic, shell=True)
                    else:
                        print("file " + f + " is cataloged")
                else:
                    print("still copying " + outList[0])

def make_single_file_inventory(file, row, rowObj, uids, header_map, args):
    '''
    generates catalog data for a single file
    '''
    fullpath = os.path.join(args.path, file)
    rowObj.row = row + 1
    rowObj.data.filename = file
    uidInFile = mfd.get_uid_from_file(fullpath)
    if uidInFile:
        rowObj.identifier = uidInFile
    else:
        rowObj.identifier = int(mtd.get_last_uid()) + 1
    args.uid = rowObj.identifier
    rowObj.data['SHA1 hash - on RAID'] = mfd.hash_file(fullpath)
    pprint(rowObj)
    if not rowObj.identifier in uids:
        print('here')
        rowObj.data.duration = mfd.get_file_duration(fullpath)
        gh.update_cell_value("A" + str(rowObj.row), rowObj.identifier, args.worksheet)
        for key, value in rowObj.data.items():
                gh.update_cell_value(header_map[key] + str(rowObj.row), value, args.worksheet)
    return rowObj

def update_catalog(rowObj, catalog_rowObj, header_map, args):
    '''
    updates catalog with data generated from file
    '''
    print("updating catalog with file info in md.update_catalog()")
    for key, value in rowObj.data.items():
        print(key)
        print("rowObj value: " + str(value))
        if value:
            catalog_value = catalog_rowObj.data[key]
            print("catalog_value: " + catalog_value)
            if not catalog_value:
                print("no catalog value found for key " + key + ", updating catalog")
                cell = header_map[key] + str(rowObj.row)
                value = rowObj.data[key]
                print("updating cell " + cell + " with value " + value)
                gh.update_cell_value(cell, value, args.worksheet)

def inventory_directory(args):
    '''
    send file data to catalog/ to_process
    get dir and filename lists from catalog - convert to list of single paths
    generate list of single paths for traffic
    if not in catalog:
    add filename, path, assign uid
    '''
    if args.it:
        args.path = args.traffic
    elif args.io:
        args.path = args.io
    print("getting list of files from " + args.path + " in md.inventory_directory()")
    for file in os.listdir(args.path):
        if not file.endswith(".zip") and not file.startswith("."):
            print("processing file " + file)
            print("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
            args = gh.get_worksheet(args)
            print("checking if file is cataloged in md.inventory_directory()")
            file_is_cataloged, header_map = mtd.is_file_cataloged(os.path.join(args.path,file), args)
            rowObj, _header_map = mtd.is_file_cataloged(os.path.join(args.path,file), args)
            pprint(file_is_cataloged)
            if file_is_cataloged:
                print("filling rowObj from filedata in md.inventory_directory()")
                rowObj = mfd.fill_rowObj_fromFile(file, rowObj, args)
                print("rowObj")
                pprint(rowObj)
                print("file_is_cataloged")
                pprint(file_is_cataloged)
                if not rowObj.identifier:
                    print("no identifier in catalog or filename, generating new uid")
                    last_uid = mtd.get_last_uid(args)
                    rowObj.identifier = str(int(last_uid) + 1)
                    print("uid is " + rowObj.identifier)
                print("sending updates to catalog in md.inventory_directory()")
                update_catalog(rowObj, file_is_cataloged, header_map, args)
                #rowObj = make_single_file_inventory(file, row, rowObj, uids, header_map, args)
    '''
    create list of fullpaths
    '''
    '''
    for f in filenames:
        thedir = dirs[filenames.index(f) - 1]
        catalog_paths.append(os.path.join(thedir,f))
    '''
    '''
    walk thru traffic/ other
    for each file in traffic/ other
    make a rowObj for the file
    inventory the file
    '''


    '''if args.ook:
            rowObj = make_rowObject.fill_rowObject_fromCatalog(rowObj, header_map, args)
            make_single_file_inventory(file, row, rowObj, uids, header_map, worksheet, args)
    else:
        if not file in filenames:
            make_single_file_inventory(file, row, rowObj, uids, header_map, worksheet, args)'''


def init():
    '''
    initialize vars
    '''
    parser = argparse.ArgumentParser(description="makes the metadata ~flow~")
    parser.add_argument('-start',dest='start', help="the start UID you want to hash")
    parser.add_argument('--moveDropboxToTraffic', dest='mdtt', action='store_true', help="moves file from Dropbox folder to traffic on NAS")
    parser.add_argument('--inventoryTraffic', dest="it", default=False, action='store_true', help="send file data from traffic to catalog")
    parser.add_argument('--inventoryOther', dest='io', default=False, help="the top-level path that you would like to inventory")
    parser.add_argument('--overwriteOK', dest='ook', action='store_true', default=False, help='allow re-upload of catalog data for existing entries')
    parser.add_argument('--sheet', dest='sheet', choices=['to_process','catalog'],default='to_process', help="the sheet in the spreadsheet to work with")
    args = parser.parse_args()
    return args

def main():
    '''
    do the thing
    '''
    print("move_data.py started at " + datetime.now())
    args = init()
    if platform == "linux" or platform == "linux2":
        args.Dropbox = "/root/Dropbox/MF archival audio"
        args.traffic = "/mnt/nas/traffic"
    elif platform == "darwin":
        args.Dropbox = "/root/Dropbox/MF archival audio"
        args.traffic = "/Volumes/NAS_Public/traffic"
    if args.it or args.io:
        inventory_directory(args)
    '''if args.mdtt is True:
        moveDropboxToTraffic(args)
        exit()
    if args.start is True:
        path = "/Volumes/My Passport/Micheal Feinstein Audio Files"
        cleanpath = "/Volumes/NAS_Public/hdd_uploads/feinstein_2014-2017_clone/compounded-objects"
        #cleaner(cleanpath, args)
        make_and_send_hash(path, args)'''

if __name__ == '__main__':
    main()
