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
  parser.add_option('--ext', dest='ext', default='', help="Running over Datacard with extension")
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

  # add this to distinguish different fits with same POI
  _name += "_"+opt.ext

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
      resfile = "higgsCombine_%s_%s.MultiDimFit.mH125.root"%(_name,poi)
      if os.path.isfile(resfile): 
        print " --> Storing ",_fit.split(":")[0],": %s/higgsCombine_%s_%s.root"%(pdir,_name,poi)
        run("mv %s %s/higgsCombine_%s_%s.root"%(resfile,pdir,_name,poi))
      if poi in ["r_ggH","r_VBF","r_top","r_VH"]:
        translate_json = "pois_mu.json" 
      elif poi=='CMS_zz4l_fai1':
        if 'ALT_0M' in opt.ext: translate_json = "pois_fa3.json"
        if 'ALT_0PH' in opt.ext: translate_json = "pois_fa2.json"
        if 'ALT_L1' in opt.ext: translate_json = "pois_flambda1.json"
        if 'ALT_L1Zg' in opt.ext: translate_json = "pois_flambda1zgamma.json"
      else:
        print "Warning: unknown poi. Use r as default"
        translate_json = "pois_mu.json"
      plotcmd = "cd %s; plot1DScan.py higgsCombine_%s_%s.root --y-cut 30 --y-max 30 -o %s_%s --POI %s --main-label %s --translate %s/src/flashggFinalFit/Plots/%s; cd .."%(pdir,_name,poi,_name,poi,poi,mainlabel,os.environ['CMSSW_BASE'],translate_json)
      print (plotcmd)
      run(plotcmd)

