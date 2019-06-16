#!/usr/bin/python

'''
creates dictionary object of file with catalog data
{
"identifier":"50000000000123",
"data":{
  "path":"",
  "FTPpath":"",
  "date":"",
  "title":"",
  "part":"",
  "ofTotal":"",
  "notes":"",
  "placeTerm_cityState":"",
  "placeterm_venue":"",
  "tableOfContents":"",
  "duration":"",
  "generation":"",
  "filename":"",
  "SHA1hash-onDrive":"",
  "SHA1hash-onRAID":""
}
}
'''
from pprint import pprint
import ghandler as gh
import argparse
import string

class dotdict(dict):
    '''
    dot["notation"] == dot.notation for dictionary attributes
    '''
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def get_header(sheet):
    '''
    returns list of header row of given sheet
    '''
    gc = gh.authorize()
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    worksheet = spreadsheet.worksheet(sheet)
    header_row = worksheet.row_values(1)
    header_column_map = make_header_column_map(header_row)
    return header_row, header_column_map

def make_header_column_map(header_row):
    '''
    maps headers to ABCD etc
    '''
    header_column_map = dotdict({})
    for header in header_row:
        _char = header_row.index(header)
        char = string.ascii_uppercase[_char]
        header_column_map[header] = char
    return header_column_map

def clean_header_row(header_row):
    '''
    removes list objects that we don't need like nameroles
    '''
    _header_row = []
    for header in header_row:
        if not header == "name" and not header == "role" and not header == "hashes match?" and not header == "showHide" and not header == "identifier":
            _header_row.append(header)
    return _header_row

def clean_header_column_map(header_column_map, header_row):
    '''
    normalized map based on clean header info
    '''
    header_map = dotdict({})
    for header in header_row:
        header_map[header] = header_column_map[header]
    return header_map

def init_rowObject(args):
    '''
    initalizes blank rowObject
    '''
    rowObj = dotdict({"identifier":"","row":"","data":{}})
    header_row, header_column_map = get_header(args.sheet)
    header_row = clean_header_row(header_row)
    header_map = clean_header_column_map(header_column_map, header_row)
    #convert list to dotdict
    for header in header_row:
        rowObj.data[header] = ""
    return rowObj, header_map

def get_identifier_column(args):
    '''
    returns list of identifiers from google sheets
    '''
    gc = gh.authorize()
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    worksheet = spreadsheet.worksheet(args.sheet)
    identifiers = worksheet.col_values(1)
    return identifiers

def fill_rowObject(rowObj, header_map, args):
    '''
    fills rowObj with data from google sheets
    '''
    identifiers = get_identifier_column(args)
    #identifiers = []
    #for id in _identifiers:
        #identifiers.append(id)
    rowObj.row = str(identifiers.index(args.uid) + 1)
    gc = gh.authorize()
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    worksheet = spreadsheet.worksheet(args.sheet)
    row = worksheet.row_values(rowObj.row)
    for name, letter in header_map.items():
        indx = ord(letter)
        print(letter)
        print(indx)
        rowObj.data[name] = row[indx - 65]
    rowObj.identifier = args.uid
    return rowObj

def init():
    '''
    inits vars from CLI
    '''
    parser = argparse.ArgumentParser(description="makes a rowObject for integrating filedata and Google Sheets")
    parser.add_argument('-sheet',choices=['catalog','to_process'],dest='sheet', help="the Google Sheet to use")
    parser.add_argument('-identifier', dest='uid', help="the uid for the file, e.g. 50000123")
    #parser.add_argument('--inventoryTraffic', dest="it", action='store_true', help="send file data from traffic to catalog")
    args = parser.parse_args()
    return args

def main():
    '''
    do the thing
    '''
    args = init()
    rowObj, header_map = init_rowObject(args)
    rowObj = fill_rowObject(rowObj, header_map, args)
    pprint(rowObj)
    print("hello world!")
    foo = dotdict({"thing":"hey"})
    print(foo.thing)


if __name__ == "__main__":
    main()
