#!/usr/bin/env python
'''
handles all google sheets calls
'''

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def authorize():
    '''
    conenct to google sheets api
    '''
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    gc = gspread.authorize(credentials)
    return gc

def make_rowdict(sh):
    '''
    returns dictionary of first row values
    '''
    rd = {}
    vals = sh.row_values(1)
    for v in vals:
        rd[v] = ''
    return rd

def get_row(sh):
    '''
    gets row values from sheet argument)
    '''
    vals = sh.row_values(1)
    return vals

def get_column(column):
    '''
    returns list of column values for supplied column letter
    '''


def insert_row(rowlist, rowdict, rownum, sh):
    '''
    inserts a row based on row1 names in rowlist
    '''
    cl = []
    cell_list = sh.range('A' + str(rownum) + ":K" + str(rownum))
    for field in rowlist:
        cl.append(rowdict[field])
    for idx, c in enumerate(cl):
            cell_list[idx].value = c.decode('utf-8', 'ignore')
    sh.update_cells(cell_list)

def main():
    '''
    do the things
    '''
    gc = authorize()
    sh = gc.open("MichaelFeinsteinArchives-Catalog").sheet1
    row = get_row(sh)
    rd = make_rowdict(row)
    print(rd)

if __name__ == '__main__':
    main()
