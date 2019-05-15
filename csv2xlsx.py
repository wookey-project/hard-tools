import sys
import os
import glob
import csv
from xlsxwriter.workbook import Workbook

csvfile = sys.argv[1]
workbook = Workbook(sys.argv[2])
worksheet = workbook.add_worksheet()
with open(csvfile) as f:
    reader = csv.reader(f)
    for r, row in enumerate(reader):
        for c, col in enumerate(row):
            worksheet.write(r, c, col)
workbook.close()
