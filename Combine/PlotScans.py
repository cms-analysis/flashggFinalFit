# Script to collect fit outputs

import os, sys
import re
from optparse import OptionParser
import glob
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PLOT SCANS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Type of fit")
  parser.add_option('--outdir', dest='outdir', default='', help="name of the output directory in plots/")
  parser.add_option('--doObserved', dest='doObserved', action="store_true", default=False, help="Fit to data")
  return parser.parse_args()
(opt,args) = get_options()

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG COLLECT FITS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def run(cmd):
  #print "%s\n"%cmd
  os.system(cmd)


# Read json file
with open( opt.inputJson ) as jsonfile: inputs = json.load(jsonfile)[opt.mode]
# Extract info
pois = inputs['pois'].split(",")
fits = inputs['fits'].split("+")

# Create plots directory in mode
pdir="plots/%s/%s"%(opt.outdir,opt.mode)
if not os.path.isdir(pdir): 
  os.system("mkdir -p %s"%pdir)
  if os.path.exists("/afs/cern.ch"): os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php "+pdir)
# Loop over fits: plot
for fidx in range(len(fits)):
  _fit = fits[fidx]
  if _fit.split(":")[2] == "all": _fitpois = pois
  else: _fitpois = _fit.split(":")[2].split(",")
  _name = "%s_%s"%(_fit.split(":")[0],_fit.split(":")[1])
  if opt.doObserved: 
    _name += "_obs"
    mainlabel = "Observed"
  else:
    mainlabel = "Expected"

  if( _fit.split(":")[0] == "bestfit" ):
    for poi in _fitpois:
      mvcmd = "mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s/%s_%s.root"%(_name,poi,pdir,_name,poi)
      print " --> Storing best fit: %s/%s_%s.root"%(pdir,_name,poi)
      run(mvcmd)

  elif( _fit.split(":")[0] == "fixed" ):
    for poi in _fitpois:
      mvcmd = "mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s/%s.root"%(pdir,_name,pdir,poi,_name)
      print " --> Storing fixed point: %s/%s.root"%(pdir,_name)
      run(mvcmd)

  elif( _fit.split(":")[0] == "profile1D")|( _fit.split(":")[0] == "scan1D" ):
    for poi in _fitpois:
      mvcmd = "mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s/higgsCombine_%s_%s.root"%(_name,poi,pdir,_name,poi)
      run(mvcmd)
      plotcmd = "cd %s; plot1DScan.py higgsCombine_%s_%s.root --y-cut 30 --y-max 30 -o %s_%s --POI %s --main-label %s --translate %s/src/flashggFinalFit/Plots/pois_mu.json; cd .."%(pdir,_name,poi,_name,poi,poi,mainlabel,os.environ['CMSSW_BASE'])
      run(plotcmd)

