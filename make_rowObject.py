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
import google_handler as gh
import make_metadata as mtd
import argparse
import string

class dotdict(dict):
    '''
    dot["notation"] == dot.notation for dictionary attributes
    '''
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def get_header(args):
    '''
    returns list of header row of given sheet
    '''
    if not args.worksheet:
        print("getting ws data in mro.get_header()")
        worksheet = gh.get_worksheet(args)
    print("retrieving header row from " + args.sheet + " in mro.get_header()")
    header_row = args.worksheet.row_values(1)
    print("creating header_column_map from " + args.sheet + " in mro.get_header()")
    header_column_map = make_header_column_map(header_row)
    print("header_row and header_column_map created in mro.get_header")
    return header_row, header_column_map

def make_header_column_map(header_row):
    '''
    maps headers to ABCD etc
    '''
    print("initializing header_column_map in mro.make_header_column_map()")
    header_column_map = dotdict({})
    print("filling header_column_map in mro.make_header_column_map()")
    for header in header_row:
        _char = header_row.index(header)
        char = string.ascii_uppercase[_char]
        header_column_map[header] = char
        print(header + ":" + char)
    print("header_column_map created in mro.make_header_column_map()")
    return header_column_map

def clean_header_row(header_row):
    '''
    removes list objects that we don't need like nameroles
    '''
    print("cleaning header_row in mro.clean_header_row()")
    _header_row = []
    for header in header_row:
        if not header == "name" and not header == "role" and not header == "hashes match?" and not header == "showHide" and not header == "identifier":
            _header_row.append(header)
    print("header_row_cleaning complete in mro.clean_header_row()")
    return _header_row

def clean_header_column_map(header_column_map, header_row):
    '''
    normalized map based on clean header info
    '''
    print("cleaning header_column_map in mro.clean_header_column_map()")
    header_map = dotdict({})
    for header in header_row:
        header_map[header] = header_column_map[header]
    print("header_column_map cleaning completed in mro.clean_header_column_map()")
    return header_map

def init_rowObject(args):
    '''
    initalizes blank rowObject and map of header -> letter mapping, e.g. identifier:A
    '''
    print("initializing rowObj in init_rowObject()")
    rowObj = dotdict({"identifier":"","row":"","data":{}})
    print("getting header_row and creating header_column_map in mro.init_rowObject()")
    header_row, header_column_map = get_header(args)
    print("header_row")
    pprint(header_row)
    print("header_column_map")
    pprint(header_column_map)
    print("cleaning header row in mro.init_rowObj()")
    header_row = clean_header_row(header_row)
    pprint(header_row)
    print("cleaning header_column_map in mro.init_rowObj()")
    header_map = clean_header_column_map(header_column_map, header_row)
    pprint(header_column_map)
    #convert list to dotdict
    print("initializing rowObj.data dotdict in mro.init_rowObject()")
    for header in header_row:
        rowObj.data[header] = ""
    rowObj.data = dotdict(rowObj.data)
    print("rowObj and header_map initialized in mro.init_rowObj")
    return rowObj, header_map

def get_row_from_uid(args):
    '''
    returns row number from Google Sheets for supplied UID
    '''
    try:
        #try assigning the index+1 of the uid in list identifiers
        row = str(identifiers.index(args.uid) + 1)
        return row
    except:
        #if it's not there, like if it's uninventoried, return False
        return False

def fill_rowObj_fromRow(rowObj, header_map, args):
    '''
    if we know the row
    grip the row data
    transform into rowObj
    '''
    print("filling rowObj with row" + str(rowObj.row) + " data from " + args.sheet + " in mro.fill_rowObj_fromRow()")
    rowData = args.worksheet.row_values(rowObj.row)
    for name, letter in header_map.items():
        indx = ord(letter)
        rowObj.data[name] = rowData[indx - 65] #assigns every key in data:{}
        rowObj.identifier = args.worksheet.acell("A" + str(rowObj.row)).value
    print("rowObj fill from row complete")
    return rowObj

def fill_rowObject_fromCatalog(rowObj, header_map, args):
    '''
    fills rowObj with data from google sheets
    '''
    gc = gh.authorize()
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    worksheet = spreadsheet.worksheet(args.sheet)
    identifiers = worksheet.col_values(1)
    rowObj.row = get_row_from_uid(args)
    if rowObj.row:
        row = worksheet.row_values(rowObj.row)
        for name, letter in header_map.items():
            indx = ord(letter)
            print(letter)
            print(indx)
            rowObj.data[name] = row[indx - 65] #assigns every key in data:{}
            rowObj.identifier = args.uid
        return rowObj
    else:
        rowObj.row = len(identifiers) + 1
        rowObj.identifier = args.uid
        return rowObj

def init():
    '''
    inits vars from CLI
    '''
    parser = argparse.ArgumentParser(description="makes a rowObject for integrating filedata and Google Sheets")
    parser.add_argument('-sheet',choices=['catalog','to_process'],dest='sheet', help="the Google Sheet to use")
    parser.add_argument('-identifier', dest='uid', default=False, help="the uid for the file, e.g. 50000123")
    #parser.add_argument('--inventoryTraffic', dest="it", action='store_true', help="send file data from traffic to catalog")
    args = parser.parse_args()
    return args

def main():
    '''
    do the thing
    '''
    args = init()
    rowObj, header_map = init_rowObject(args)
    pprint(header_map)
    rowObj = fill_rowObject_fromCatalog(rowObj, header_map, args)
    pprint(rowObj)


if __name__ == "__main__":
    main()
