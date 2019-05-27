#!/usr/bin/env python

'''
data_mover.py

moves data on disc
moves data to / from google sheets
'''

import re
import ghandler as gh
import gspread
import subprocess

def hash_file(filepath):
    '''
    uses shasum to create SHA1 hash of file
    '''
    output = subprocess.check_output("shasum " + filepath, shell=True)
    match = ''
    #search for 40 consecutive word characters in string, convert byte output from shasum in CLI to utf-8 string
    match = re.search(r'\w{40}', output.decode("utf-8"))
    if match:
        #convert match object to string
        thehash= match.group()
        return thehash
    else:
        return "hash error"

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

def main():
    '''
    do the thing
    '''
    gc = gh.authorize()
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    worksheet = spreadsheet.worksheet("catalog")
    #thecell = gh.find_cell('50000000000000',worksheet)
    #print(thecell.row)
    filepath = "/Volumes/thedata/brnco/Desktop/50000000000002_Jun-23-1980_Cabaret-Nightclub_01_prod.wav"
    thehash = hash_file(filepath)
    uid = get_uid_from_file(filepath)
    sheets_uid_match = gh.find_cell(uid, worksheet)
    gh.update_cell_value("M" + str(sheets_uid_match.row), thehash, worksheet)

if __name__ == '__main__':
    main()
