# Script to collect fit outputs

import os, sys
import re
from optparse import OptionParser
import glob
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG COLLECT FITS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Type of fit")
  parser.add_option('--ext', dest='ext', default='', help="If txt datacard has extension")
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
if not os.path.isdir("runFits%s_%s/Plots"%(opt.ext,opt.mode)): os.system("mkdir runFits%s_%s/Plots"%(opt.ext,opt.mode))
# Loop over fits: hadd and then plot
for fidx in range(len(fits)):
  _fit = fits[fidx]
  if _fit.split(":")[2] == "all": _fitpois = pois
  else: _fitpois = _fit.split(":")[2].split(",")
  _name = "%s_%s"%(_fit.split(":")[0],_fit.split(":")[1])
  if opt.doObserved: _name += "_obs"

  if( _fit.split(":")[0] == "bestfit" ):
    for poi in _fitpois:
      mvcmd = "cd runFits%s_%s; mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s_%s.root; cd .."%(opt.ext,opt.mode,_name,poi,_name,poi)
      print " --> Storing best fit: runFits%s_%s/%s_%s.root"%(opt.ext,opt.mode,_name,poi)
      run(mvcmd)

  elif( _fit.split(":")[0] == "fixed" ):
    for poi in _fitpois:
      mvcmd = "cd runFits%s_%s; mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s.root; cd .."%(opt.ext,opt.mode,_name,poi,_name)
      print " --> Storing fixed point: runFits%s_%s/%s.root"%(opt.ext,opt.mode,_name)
      run(mvcmd)

  elif( _fit.split(":")[0] == "profile1D")|( _fit.split(":")[0] == "scan1D" ):
    for poi in _fitpois:
      haddcmd = "cd runFits%s_%s; hadd -f %s_%s.root higgsCombine_%s_%s.POINTS.*.*.root; cd .."%(opt.ext,opt.mode,_name,poi,_name,poi)
      run(haddcmd)
      plotcmd = "cd runFits%s_%s; plot1DScan.py %s_%s.root --y-cut 20 --y-max 20 -o Plots/%s_%s%s --POI %s; cd .."%(opt.ext,opt.mode,_name,poi,_name,poi,opt.ext,poi)
      run(plotcmd)

  elif( _fit.split(":")[0] == "scan2D")|( _fit.split(":")[0] == "profile2D" ):
    _poisStr = "%s_vs_%s"%(_fitpois[0],_fitpois[1])
    haddcmd = "cd runFits%s_%s; hadd -f %s_%s.root higgsCombine_%s_%s.POINTS.*.*.root; cd .."%(opt.ext,opt.mode,_name,_poisStr,_name,_poisStr)
    run(haddcmd)
    
