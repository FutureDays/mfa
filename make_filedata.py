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
    loggr("attempting to locate uid in file name in mfd.get_uid_from_file")
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
    loggr('attempting to hash file ' + filepath)
    print('attempting to hash file ' + filepath)
    try:
        output = subprocess.check_output("shasum '" + filepath + "'", shell=True)
    except subprocess.CalledProcessError as e:
        return False
    match = ''
    #search for 40 consecutive word characters in string, convert byte output from shasum in CLI to utf-8 string
    match = re.search(r'\w{40}', output.decode("utf-8"))
    if match:
        #convert match object to string
        thehash= match.group()
        loggr("file " + os.path.basename(filepath) + " hash is " + thehash)
        print("file " + os.path.basename(filepath) + " hash is " + thehash)
        return thehash
    else:
        return False

def fill_rowObj_fromFile(fullpath, rowObj, args):
    '''
    fills rowObj with info from file
    '''
    file = os.path.basename(fullpath)
    duration = rowObj['data']['duration']
    loggr(duration)
    print(duration)
    if not duration:
        loggr("no duration in catalog, getting duration of " + file)
        print("no duration in catalog, getting duration of " + file)
        rowObj.data.duration = get_file_duration(fullpath)
    if "nas" in fullpath or "NAS" in fullpath:
        whichHash = 'SHA1hash-onRAID'
    else:
        whichHash = 'SHA1hash-ondrive'
    hash = rowObj.data[whichHash]
    if not hash:
        loggr("no hash in catalog, hashing " + file)
        print("no hash in catalog, hashing " + file)
        rowObj.data[whichHash] = hash_file(fullpath)
        if not rowObj.data[whichHash]:
            loggr("hash error")
            print("hash error")
    uid = rowObj.identifier
    if not uid:
        loggr("identifier not in rowObj, attempting to locate uid in filename in mfd.fill_rowObj_fromFile()")
        print("identifier not in rowObj, attempting to locate uid in filename in mfd.fill_rowObj_fromFile()")
        rowObj.identifier = get_uid_from_file(fullpath)
    return rowObj

def make_rowObj(args):
    '''
    use make_rowObject to make a rowObj
    '''
    rowObj, header_map = make_rowObject.init_rowObject(args)
    rowObj = make_rowObject.fill_rowObject_fromCatalog(rowObj, header_map, args)
    loggr(rowObj)
    return rowObj

if __name__ == '__main__':
    print("make_filedata has no standalone functions")
    print("perhaps you meant to run move_data.py?")
