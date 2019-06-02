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
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
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

def get_row_values(worksheet):
    '''
    gets row values from sheet argument
    '''
    vals = worksheet.row_values(1)
    return vals

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

def main():
    '''
    do the things
    '''
    gc = authorize()
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1R7cYjCFdpwTbWYouUNOa_E72kJ9B8fJfeO6MEHiRZ4M/edit#gid=0")
    worksheet = spreadsheet.worksheet("catalog")
    #row = get_row_values(worksheet)
    #update_cell_value('M2',worksheet)
    thecell = find_cell('50000000000000',worksheet)
    print(thecell.row)

if __name__ == '__main__':
    main()
