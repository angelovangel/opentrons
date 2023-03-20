# this script reads the xlsx and writes the source/dest wells and volumes to protocol.py, gui version
# execute from within the bin folder!

from easygui import *
import tkinter
from tkinter import filedialog
import pandas as pd
import time
import re
import os
    
cwd = os.getcwd()


tkinter.Tk().withdraw() 
protocolpath=filedialog.askopenfilename(title="Select file - python protocol template", 
                                        defaultextension= '*.py', 
                                        initialdir = '../protocols')
#protocolpath = fileopenbox("Select python protocol template", "Select file", default='*.py') # crashes!!!
xlpath = filedialog.askopenfilename(title='Select file - excel file with data for the protocol', 
                                    defaultextension= '*.xlsx', 
                                    initialdir= '../templates',)
#xlpath = fileopenbox("excel file with data for the protocol", "Select file", default='*.xlsx', )
sheet = integerbox("Select which excel sheet to read", "Select sheet", default= 5, lowerbound=0, upperbound=10)
#print(protocolpath)

df = pd.read_excel(xlpath, header = 0, sheet_name=sheet)
df.fillna(" ", inplace=True)
xlcolumns = df.columns.tolist()

# read script
with open(protocolpath, 'r') as file:
    txt = file.read()

# do work here ########################################
replacements = 0
notfound = 0

for i, v in df.iteritems():
    search_pattern = "^" + i + "=\[.*"
    replacement = i + "=" + str(v.tolist())
    
    # repair well names of replacement
    replacement = re.sub(r'([A-Z])0+(\d+)', r'\1\2', replacement)

    found = re.search(search_pattern, txt, flags=re.MULTILINE)
    if found:
        txt = re.sub(search_pattern, replacement, txt, flags=re.MULTILINE) # the flag is needed for ^ to work
        replacements += 1
    else:
        #print(f"{i} was not found at the beginning of any line in {args.txtfile}")
        notfound += 1
        
     
timestring = time.strftime("%Y%m%d-%H%M%S")

with open('../runprotocols/' + timestring + '-protocol.py', 'x') as file:
        file.write(txt)

msgbox( "Done. Use runprotocols/" +  timestring + "-protocol.py to run the OT2" )
