# this script reads the 01-Sanger-master.xlsx and writes the source/dest wells and volumes to Sanger-template.py

import easygui
import tkinter
from tkinter import filedialog
import pandas as pd
import time
import re
    

tkinter.Tk().withdraw() 
path=filedialog.askopenfilename()

df = pd.read_excel(path, header = 0, sheet_name=5)
df.fillna(" ", inplace=True)
xlcolumns = df.columns.tolist()

# read script
with open('protocols/Sanger-setup-BCL.py', 'r') as file:
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

with open('Sanger-' + timestring + '.py', 'x') as file:
        file.write(txt)

easygui.msgbox ( "Done. Use Sanger-" +  timestring + ".py to run the OT2")
