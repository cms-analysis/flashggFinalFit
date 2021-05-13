# Script to determine diagonal process for each category and write to json file

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG GET DIAG PROC RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
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

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG GET DIAG PROC RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--inputWSDir', dest='inputWSDir', default='', help='Input WS directory')
  parser.add_option('--ext', default='test', help='Extension (to define analysis)')
  parser.add_option('--MH', dest='MH', default='125', help='MH')
  parser.add_option('--makeSimpleFTest', dest='makeSimpleFTest', default=False, action="store_true", help='Produce simple fTest json with diagonal proc values set to nRV,nWV (else=1,1)')
  parser.add_option('--nRV', dest='nRV', default='3', help='Number of gaussians for diag proc (RV)')
  parser.add_option('--nWV', dest='nWV', default='1', help='Number of gaussians for diag proc (WV)')
  return parser.parse_args()
(opt,args) = get_options() 

# Extract all processed analysis categories
WSFileNames = extractWSFileNames(opt.inputWSDir)
if not WSFileNames: leave()
allProcs = extractListOfProcs(WSFileNames)
allCats = extractListOfCats(WSFileNames)

dproc, dsumw = {}, {}
for cat in allCats.split(","):
  dproc[cat] = None
  dsumw[cat] = 0.

# Loop over procs
for proc in allProcs.split(","):
  print " --> Processing: %s"%proc
  # Open workspace
  _WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,opt.MH,proc))[0]
  f = ROOT.TFile(_WSFileName,'read')
  inputWS = f.Get(inputWSName__)

  # Loop over cats: up
  for cat in allCats.split(","):
    # Extract sum of weights
    nominalDataName = "%s_%s_%s_%s"%(procToData(proc.split("_")[0]),opt.MH,sqrts__,cat)
    nominalData = inputWS.data(nominalDataName)
    sumw = nominalData.sumEntries()
    # Update dict if largest
    if sumw > dsumw[cat]:
      dsumw[cat] = sumw
      dproc[cat] = proc

  # Close workspace
  inputWS.Delete()
  f.Close()

# Save json file
print " --> Writing diagonal processes to json file\n"
if not os.path.isdir("%s/outdir_%s/getDiagProc/json"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/getDiagProc/json"%(swd__,opt.ext))
with open("%s/outdir_%s/getDiagProc/json/diagonal_process.json"%(swd__,opt.ext),"w") as jf: json.dump(dproc,jf)

# One json file for each cat: diagonal proc first line in file
if opt.makeSimpleFTest:
  print " --> Making simple fTest config json using diagonal procs (nRV,nWV) = (%s,%s)"%(opt.nRV,opt.nWV)
  if not os.path.isdir("%s/outdir_%s/fTest"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/fTest"%(swd__,opt.ext))
  if not os.path.isdir("%s/outdir_%s/fTest/json"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/fTest/json"%(swd__,opt.ext))
  for cidx, cat in enumerate(allCats.split(",")):
    ff = open("%s/outdir_%s/fTest/json/nGauss_%s.json"%(swd__,opt.ext,cat),"w")
    ff.write("{\n")
    pitr = 1
    # First write diagonal proc
    k = "\"%s__%s\""%(dproc[cat],cat)
    ff.write("    %-90s : {\"nRV\":%s,\"nWV\":%s}"%(k,opt.nRV,opt.nWV))
    if pitr == len(allProcs.split(",")): ff.write("\n")
    else: ff.write(",\n")
    pitr += 1
    # Then other process
    for pidx, proc in enumerate(allProcs.split(",")):
      k = "\"%s__%s\""%(proc,cat)
      if proc == dproc[cat]: continue
      else: ff.write("    %-90s : {\"nRV\":1,\"nWV\":1}"%k)
      # Drop comma for last entry
      #if pitr == (len(allProcs.split(","))-1): ff.write("\n")
      if pitr == len(allProcs.split(",")): ff.write("\n")
      else: ff.write(",\n")
      pitr += 1
    ff.write("}")
    ff.close()
