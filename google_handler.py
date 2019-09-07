#!/usr/bin/env python
'''
handles all google sheets calls
'''

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def authorize():
    '''
    connect to google sheets api
    '''
    print("authorizing in gh.authorize()")
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
    print("getting credentials from client_secret.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    print("authorizing...")
    gc = gspread.authorize(credentials)
    print("authorization complete")
    return gc

def get_worksheet(args):
    '''
    returns worksheet
    '''
    print("authorizing ws in gs.get_worksheet()")
    gc = authorize()
    print("retrieving spreadsheet data in gs.get_worksheet()")
    args.spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    print("retrieving worksheet data from " + args.sheet + " in gs.get_worksheet()")
    args.worksheet = args.spreadsheet.worksheet(args.sheet)
    return args

def make_rowdict(sh):
    '''
    returns dictionary of first row values
    '''
    rd = {}
    vals = sh.row_values(1)
    for v in vals:
        rd[v] = ''
    return rd

def get_row_values(worksheet):
    '''
    gets row values from sheet argument
    '''
    vals = worksheet.row_values(1)
    return vals

def get_column_values(columnLetter, worksheet):
    '''
    returns list of column values
    '''
    col = ord(columnLetter) - 64
    vals = worksheet.col_values(col)
    return vals

def get_cell_value(cell, worksheet):
    '''
    returns value of a cell
    '''
    cell_value = worksheet.acell(cell).value
    return cell_value

def update_cell_value(cell, value, worksheet):
    '''
    updates the value of a cell
    '''
    worksheet.update_acell(cell, value)

def find_cell(stringquery, worksheet):
    '''
    finds a cell containing stringquery
    '''
    cell = worksheet.find(stringquery)
    return cell

def cell_is_empty(cell, worksheet):
    '''
    returns True if cell is empty
    '''
    cell_value = worksheet.acell(cell).value
    if cell_value:
        return False
    else:
        return True

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

if __name__ == '__main__':
    print("google_handler has no standalone functions")
    print("perhaps you meant to run move_data.py?")
