# Script to determine diagonal process for each category and write to json file

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG GET DIAG PROC RUN III ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
from collections import OrderedDict as od

from commonTools import *
from commonObjects import *
from XSBRMap import *

def leave():
  print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG GET DIAG PROC RUN III (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--inputParquetDir', dest='inputParquetDir', default='', help='Input parquet directory')
  parser.add_option('--cats', dest='cats', default='', help='Comma separated list of categories to process')
  parser.add_option('--sort-by', dest='sort_by', default='yield', help='Pick diagonal process by "yield" or "sumw"')
  parser.add_option('--ext', dest='ext', default='', help='Extension')
  return parser.parse_args()
(opt,args) = get_options() 

# Loop over parquet files and extract yields for each proc x cat
files = glob.glob("%s/events__*.parquet"%(opt.inputParquetDir))
yield_dict = {}
sumw_dict = {}
for f in files:
  proc = f.split("__")[-1].replace(".parquet","")
  # Open file and store sumw and yield for each cat
  df = pd.read_parquet(f)
  for cat in opt.cats.split(","):
    dfcat = df[df['category']==cat]
    sumw = dfcat['weight'].sum()
    y = globalXSBRMap['HIG-25-020'][proc]['factor']*sumw
    # Store in dict
    if cat not in yield_dict.keys(): yield_dict[cat] = {}
    if cat not in sumw_dict.keys(): sumw_dict[cat] = {}
    yield_dict[cat][proc] = y
    sumw_dict[cat][proc] = sumw

# For each category --> pick diagonal process based on yield or sumw
diag_proc_dict = {}
for cat in opt.cats.split(","):
  if opt.sort_by == 'yield':
    diag_proc = max(yield_dict[cat], key=yield_dict[cat].get)
  elif opt.sort_by == 'sumw':
    diag_proc = max(sumw_dict[cat], key=sumw_dict[cat].get)
  else:
    print("[ERROR] Invalid option for --sort-by: %s. Must be 'yield' or 'sumw'"%(opt.sort_by))
    leave()
  diag_proc_dict[cat] = diag_proc

# Save to json file
outname = "%s/outdir_%s/getDiagProc/json/diagonal_process.json"%(swd__,opt.ext)
if not os.path.isdir("%s/outdir_%s/getDiagProc/json"%(swd__,opt.ext)): os.system("mkdir -p %s/outdir_%s/getDiagProc/json"%(swd__,opt.ext))
with open(outname, 'w') as f:
  json.dump(diag_proc_dict, f, indent=4)


