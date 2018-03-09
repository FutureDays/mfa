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
    sh = gc.open("mfa_descriptiveMetadata").sheet1
    rd = make_rowdict(sh)
    print(rd)

if __name__ == '__main__':
    main()
