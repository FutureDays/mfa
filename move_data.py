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
from logger import log as loggr

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
        loggr("mount the NAS before continuing!", **{"level":"error"})
        print("mount the NAS before continuing!")
        exit()
    loggr("args.Dropbox is " + args.Dropbox)
    for dirs, subdirs, files in os.walk(args.Dropbox):
        for file in files:
            if not "." in file:
                continue
            elif not ".tmp" in file and not file.startswith("."):
                loggr("processing file " + file)
                print("processing file " + file)
                fullpath = os.path.join(dirs, file)
                with cd(args.Dropbox):
                    output = subprocess.check_output('dropbox filestatus "' + file + '"', shell=True)
                    output = output.decode("utf-8")
                    loggr(output)
                #output = "/root/Dropbox/MF archival audio/20170225_PalmDesertAct2_T585.mp3: up to date"
                outList = output.split(":")
                status = outList[1].lstrip()
                loggr(status)
                if "up to date" in status:
                    loggr("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
                    print("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
                    args = gh.get_worksheet(args)
                    loggr("checking if file is cataloged in md.inventory_directory()")
                    print("checking if file is cataloged in md.inventory_directory()")
                    file_is_cataloged, header_map = mtd.is_file_cataloged(os.path.join(args.Dropbox,file), args)
                    loggr(file_is_cataloged)
                    if not file_is_cataloged:
                        loggr("file is not cataloged")
                        print("file is not cataloged")
                        loggr("copying " + file)
                        print("copying " + file)
                        subprocess.check_output('rsync -av --progress "' + fullpath + '" ' + args.traffic, shell=True)
                    else:
                        loggr("file " + file + " is cataloged")
                        print("file " + file + " is cataloged")
                else:
                    loggr("still copying " + outList[0])
                    print("still copying " + outList[0])
            loggr("resting 30s for API reset")
            print("resting 30s for API reset")
            time.sleep(30)

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
    loggr(rowObj)
    if not rowObj.identifier in uids:
        rowObj.data.duration = mfd.get_file_duration(fullpath)
        gh.update_cell_value("A" + str(rowObj.row), rowObj.identifier, args.worksheet)
        for key, value in rowObj.data.items():
                gh.update_cell_value(header_map[key] + str(rowObj.row), value, args.worksheet)
    return rowObj

def update_catalog(rowObj, catalog_rowObj, header_map, args):
    '''
    updates catalog with data generated from file
    '''
    loggr("updating catalog with file info in md.update_catalog()")
    print("updating catalog with file info in md.update_catalog()")
    for key, value in rowObj.data.items():
        loggr(key)
        loggr("rowObj value: " + str(value))
        if value:
            catalog_value = catalog_rowObj.data[key]
            loggr("catalog_value: " + catalog_value)
            if not catalog_value:
                loggr("no catalog value found for key " + key + ", updating catalog")
                print("no catalog value found for key " + key + ", updating catalog")
                cell = header_map[key] + str(rowObj.row)
                value = rowObj.data[key]
                loggr("updating cell " + cell + " with value " + value)
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
    loggr("getting list of files from " + args.path + " in md.inventory_directory()")
    print("getting list of files from " + args.path + " in md.inventory_directory()")
    for file in os.listdir(args.path):
        if not file.endswith(".zip") and not file.startswith("."):
            loggr("processing file " + file)
            print("processing file " + file)
            loggr("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
            print("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
            args = gh.get_worksheet(args)
            loggr("checking if file is cataloged in md.inventory_directory()")
            print("checking if file is cataloged in md.inventory_directory()")
            file_is_cataloged, header_map = mtd.is_file_cataloged(os.path.join(args.path,file), args)
            rowObj, _header_map = mtd.is_file_cataloged(os.path.join(args.path,file), args)
            loggr(file_is_cataloged)
            if file_is_cataloged:
                loggr("filling rowObj from filedata in md.inventory_directory()")
                print("filling rowObj from filedata in md.inventory_directory()")
                rowObj = mfd.fill_rowObj_fromFile(file, rowObj, args)
                loggr("rowObj")
                loggr(rowObj)
                loggr("file is cataloged")
                print("file_is_cataloged")
                loggr(file_is_cataloged)
                if not rowObj.identifier:
                    loggr("no identifier in catalog or filename, generating new uid")
                    print("no identifier in catalog or filename, generating new uid")
                    last_uid = mtd.get_last_uid(args)
                    rowObj.identifier = str(int(last_uid) + 1)
                    loggr("uid is " + rowObj.identifier)
                    print("uid is " + rowObj.identifier)
                loggr("sending updates to catalog in md.inventory_directory()")
                print("sending updates to catalog in md.inventory_directory()")
                update_catalog(rowObj, file_is_cataloged, header_map, args)

def init():
    '''
    initialize vars
    '''
    loggr("initializing variables")
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
    loggr("move_data.py started at " + str(datetime.now()))
    print("move_data.py started at " + str(datetime.now()))
    args = init()
    if platform == "linux" or platform == "linux2":
        args.Dropbox = "/root/Dropbox/MF archival audio"
        args.traffic = "/mnt/nas/traffic"
    elif platform == "darwin":
        args.Dropbox = "/root/Dropbox/MF archival audio"
        args.traffic = "/Volumes/NAS_Public/traffic"
    loggr(args)
    if args.it or args.io:
        inventory_directory(args)
    if args.mdtt:
        moveDropboxToTraffic(args)
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
