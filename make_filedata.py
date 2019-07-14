#!/usr/bin python
'''
grips all file data
returns dictionary of file data
'''

import os
import re
from pprint import pprint
import argparse
import make_rowObject
import contextlib
import wave
import time
import subprocess
from mutagen.mp3 import MP3

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
    print("attempting to locate uid in file name in mfd.get_uid_from_file")
    match = ''
    match = re.search(r'\d{14}', filepath)
    if match:
        uid = match.group()
        print("uid is " + uid)
        return uid
    else:
        return False

def hash_file(filepath):
    '''
    uses shasum to create SHA1 hash of file
    '''
    print('attempting to hash file ' + filepath)
    output = subprocess.check_output("shasum '" + filepath + "'", shell=True)
    match = ''
    #search for 40 consecutive word characters in string, convert byte output from shasum in CLI to utf-8 string
    match = re.search(r'\w{40}', output.decode("utf-8"))
    if match:
        #convert match object to string
        thehash= match.group()
        print("file " + os.path.basename(filepath) + " hash is " + thehash)
        return thehash
    else:
        return False

def fill_rowObj_fromFile(file, rowObj, args):
    '''
    fills rowObj with info from file
    '''
    fullpath = os.path.join(args.path, file)
    duration = rowObj['data']['duration']
    print(type(duration))
    print(len(duration))
    print(duration)
    if not duration:
        print("no duration in catalog, getting duration of " + file)
        rowObj.data.duration = get_file_duration(fullpath)
    hash = rowObj.data['SHA1 hash - on RAID']
    print(len(hash))
    if not hash:
        print("no hash in catalog, hashing " + file)
        rowObj.data['SHA1 hash - on RAID'] = hash_file(fullpath)
        if not rowObj.data['SHA1 hash - on RAID']:
            print("hash error")
    '''
    if not rowObj.data['SHA1 hash - on drive']:
        if not args.path ==
        print("no hash in catalog, hashing " + file)
        rowObj.data['SHA1 hash - on drive'] = hash_file(fullpath)
        if not rowObj.data['SHA1 hash - on RAID']:
            print("hash error")
    '''
    uid = rowObj.identifier
    if not uid:
        print("identifier not in rowObj, attempting to locate uid in filename in mfd.fill_rowObj_fromFile()")
        rowObj.identifier = get_uid_from_file(fullpath)
    return rowObj

def make_rowObj(args):
    '''
    use make_rowObject to make a rowObj
    '''
    rowObj, header_map = make_rowObject.init_rowObject(args)
    rowObj = make_rowObject.fill_rowObject_fromCatalog(rowObj, header_map, args)
    pprint(rowObj)
    return rowObj

def init():
    '''
    inits vars from CLI
    '''
    parser = argparse.ArgumentParser(description="makes a rowObject for integrating filedata and Google Sheets")
    parser.add_argument('-sheet',choices=['catalog','to_process'],dest='sheet', help="the Google Sheet to use")
    parser.add_argument('-identifier', dest='uid', help="the uid for the file, e.g. 50000123")
    parser.add_argument('-filepath', dest='filepath', help="the path to the file you want to work on")
    #parser.add_argument('--inventoryTraffic', dest="it", action='store_true', help="send file data from traffic to catalog")
    args = parser.parse_args()
    return args

def main():
    '''
    do the thing
    '''
    args = init()
    rowObj = make_rowObj(args)
    rowObj = fill_rowObj_fromFile(rowObj, args)

if __name__ == '__main__':
    main()