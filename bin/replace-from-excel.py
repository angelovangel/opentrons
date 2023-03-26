
from os import times
import pandas as pd
import argparse
import re
import time

parser = argparse.ArgumentParser(description='Replace lines defining lists (in a python file) with data read from Excel. Uses column headers as search pattern. Useful for changing wells/volumes in Opentrons scripts.', 
                                epilog='author: aangeloo@gmail.com')
parser.add_argument('xlfile',  
                    type = str, 
                    help = 'path to excel file, will be used for replacements')
parser.add_argument('txtfile',
                     type = str, 
                     help = 'path to txt file, lines matching col headers in the excel file will be replaced')
parser.add_argument('-n', '--sheet', 
                    help='Excel sheet to be used for reading data, default is 5. Sheet numbering is 0-based.', 
                    default = 5, type = int)
parser.add_argument('-f', '--fillna', help = 'fill NaN values, will be parsed as str', default = " ")
parser.add_argument('-c', '--confirm', action = 'store_true', help = 'ask for confirmation for each replacement')
parser.add_argument('-o', '--overwrite', action = 'store_true', help = 'overwrite original txt file? (default is write to a new file with a datetime stamp)')
parser.add_argument('-r', '--repair_wells', action = 'store_true', help = 'repair well names to fit Opentrons, e.g. A01 to A1', default = True)

args = parser.parse_args()

# read excel in df
df = pd.read_excel(args.xlfile, header = 0, sheet_name=args.sheet)
if args.fillna:
    df.fillna(args.fillna, inplace = True)

xlcolumns = df.columns.tolist()

# read script
with open(args.txtfile, 'r') as file:
    txt = file.read()

### Message ################################
print(f"Will search for lines starting with {xlcolumns} in {args.txtfile}\n")
### Message ################################

# do work here
replacements = 0
notfound = 0
skipped = 0

for i, v in df.iteritems():
    search_pattern = "^" + i + "=\[.*"
    replacement = i + "=" + str(v.tolist())
    
    if args.repair_wells:
        replacement = re.sub(r'([A-Z])0+(\d+)', r'\1\2', replacement)

    found = re.search(search_pattern, txt, flags=re.MULTILINE)
    if found:
        print(f"Found  : {found.group()}") # the group method returns the actual match
        print(f"Replace: {replacement}")
        if args.confirm:
            user_input = input("press enter to continue, press 's' and then enter to skip this replacement\n")
            if user_input == "s": 
                skipped += 1
                continue
        txt = re.sub(search_pattern, replacement, txt, flags=re.MULTILINE) # the flag is needed for ^ to work
        replacements += 1
    else:
        print(f"{i} was not found at the beginning of any line in {args.txtfile}")
        notfound += 1

# summary
print(f"{replacements} lines were replaced, {skipped} were skipped and {notfound} patterns were not found")

timestring = time.strftime("%Y%m%d-%H%M%S")
#print(txt)
if args.overwrite:
    with open(args.txtfile, 'w') as file:
        file.write(txt)
        print(f"{args.txtfile} was updated with values from {args.xlfile}")
else:
    with open(timestring + '-protocol.py', 'x') as file:
        file.write(txt)
        print(f"New protocol file created: {timestring}-protocol.py")