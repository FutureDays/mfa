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
import hashlib
import configparser
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

def iterate_hash_column(column, rownumber, index):
    '''
    uhhh makes looping through the hash column possible
    '''
    for hash in column[rownumber:]:
        if not hash:
            row = column[rownumber:].index(hash) + 1 + rownumber
            index = column.index(hash)
    return row, index


def hasher(path, args):
    '''
    handler for hashing all the files
    get column of hash values
    get row number for each empty cell
    get fullpath for file represented by row
    send to process single file
    '''
    header_row, header_column_map = make_rowObject.get_header(args)
    pprint(header_column_map)
    if "nas" in args.hasher or "NAS" in args.hasher:
        columnLetter = header_column_map['SHA1hash-onRAID']
    else:
        columnLetter = header_column_map['SHA1hash-ondrive']
    print(columnLetter)
    column = gh.get_column_values(columnLetter, args.worksheet)
    #column = _column[args.start:]
    index = 0
    while index < len(column):
        gc = gh.authorize()
        row, index = iterate_hash_column(column, args.start, index)
        print(row)
        print(index)
        #verify that file which needs hash is in directory we're hashing
        _filepath = gh.get_cell_value(header_column_map['RAID-dir'] + str(row), args.worksheet)
        if _filepath.startswith("/") or _filepath.startswith(r"\\"):
            _filepath = _filepath[1:]
        filepath = os.path.join(args.nas, _filepath)
        print(int(hashlib.sha1(filepath.encode("utf-8")).hexdigest(), 16) % (10 ** 8))
        print(int(hashlib.sha1(path.encode("utf-8")).hexdigest(), 16) % (10 ** 8))
        if filepath == path:
            cell = columnLetter + str(row)
            filename = gh.get_cell_value(header_column_map['filename'] + str(row), args.worksheet)
            print(filename)
            value = mfd.hash_file(os.path.join(path, filename))
            if not value:
                value = False
            gh.update_cell_value(cell, value, args.worksheet)
            time.sleep(30)
            column = gh.get_column_values(columnLetter, args.worksheet)
        else:
            print("hasher has completed hashing direcory")
            print("next file that needs hash in catalog is:")
            print(row)
            return



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

def process_single_file(fullpath, args):
    '''
    runs a single file through the process
    '''
    loggr("processing file " + os.path.basename(fullpath))
    print("processing file " + os.path.basename(fullpath))
    loggr("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
    print("retrieving worksheet " + args.sheet + " in md.inventory_directory()")
    args = gh.get_worksheet(args)
    loggr("checking if file is cataloged in md.inventory_directory()")
    print("checking if file is cataloged in md.inventory_directory()")
    file_is_cataloged, header_map = mtd.is_file_cataloged(fullpath, args)
    rowObj, _header_map = mtd.is_file_cataloged(fullpath, args)
    loggr(file_is_cataloged)
    pprint(file_is_cataloged)
    if file_is_cataloged:
        if rowObj.data.filedata_complete == 'FALSE':
            loggr("filling rowObj from filedata in md.inventory_directory()")
            print("filling rowObj from filedata in md.inventory_directory()")
            rowObj = mfd.fill_rowObj_fromFile(fullpath, rowObj, args)
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

def inventory_directory(args):
    '''
    send file data to catalog
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
    for dirs, subdirs, files in os.walk(args.path):
        for file in files:
            if not file.endswith(".zip") and not file.startswith(".") and not file.endswith(".xml"):
                if args.start:
                    if int(args.start) <= int(file[:14]):
                        process_single_file(os.path.join(dirs,file), args)
                        loggr("sleeping for 60s for API reset")
                        print("sleeping for 60s for API reset")
                        time.sleep(60)
                    else:
                        continue
                else:
                    process_single_file(os.path.join(dirs,file), args)
                    loggr("sleeping for 60s for API reset")
                    print("sleeping for 60s for API reset")
                    time.sleep(60)

def init():
    '''
    initialize vars
    '''
    loggr("initializing variables")
    parser = argparse.ArgumentParser(description="makes the metadata ~flow~")
    parser.add_argument('--moveDropboxToTraffic', dest='mdtt', action='store_true', help="moves file from Dropbox folder to traffic on NAS")
    parser.add_argument('--inventoryTraffic', dest="it", default=False, action='store_true', help="send file data from traffic to catalog")
    parser.add_argument('--inventoryOther', dest='io', default=False, help="the top-level path that you would like to inventory")
    parser.add_argument('--overwriteOK', dest='ook', action='store_true', default=False, help='allow re-upload of catalog data for existing entries')
    parser.add_argument('--start', dest='start', type=int, default=0, help="the starting row number number")
    parser.add_argument('--hasher', dest="hasher", help="hash all the files in a directory")
    args = parser.parse_args()
    return args

def main():
    '''
    do the thing
    '''
    loggr("move_data.py started at " + str(datetime.now()))
    print("move_data.py started at " + str(datetime.now()))
    args = init()
    args.sheet = 'catalog'
    if platform == "linux" or platform == "linux2":
        args.Dropbox = "/root/Dropbox/MF archival audio"
        args.traffic = "/mnt/nas/traffic"
        args.nas = "/mnt/nas"
    elif platform == "darwin":
        args.Dropbox = "/root/Dropbox/MF archival audio"
        args.traffic = "/Volumes/NAS_Public/traffic"
        args.nas = "/Volumes/NAS_Public"
    loggr(args)
    if args.hasher:
        args = gh.get_worksheet(args)
        hasher(args.hasher, args)
    if args.it or args.io:
        inventory_directory(args)
    if args.mdtt:
        try:
            moveDropboxToTraffic(args)
        except:
            loggr("moveDropboxToTraffic didn't work :(")

if __name__ == '__main__':
    main()
