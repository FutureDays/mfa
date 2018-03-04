import os
import csv

file = "/Volumes/thedata/brnco/Desktop/mfs-hard-drives1-mtd-from_memnon.csv"

with open(file,'rb') as csvfile:
	reader = csv.reader(csvfile,delimiter=',')
	for row in reader:
		#if not any(val in (None, "") for val in row.itervalues()):
		fname = ''
		for cell in row:
			if cell is row[0]:
				continue
			if cell:
				if not fname:
					fname = cell.replace(" ","-")
				else:
					fname = fname + "_" + cell.replace(" ","-")
		fname = fname + "_" + row[0].replace(".mp4","")
		print fname