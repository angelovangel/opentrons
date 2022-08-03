
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Read Excel file and print data as lists')

parser.add_argument('file',  type = str, help = "path to excel file")
parser.add_argument('-d', '--details', 
                    action='store_true', 
                    help = 'print details about the columns of the excel sheet (name, length, type)')
parser.add_argument('-f', '--fillna', help = 'fill NaN values')

args = parser.parse_args()

df = pd.read_excel(args.file, header = 0)

if args.fillna:
    df.fillna(args.fillna, inplace = True)

if args.details:
    for (i,v) in df.iteritems():
        print(i, str(len(v)) , v.dtypes, v.to_list())
else:
    for (i,v) in df.iteritems():
        print(v.to_list())