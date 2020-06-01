# Script to submit fit jobs

import os, sys
import re
from optparse import OptionParser
import glob
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SUBMIT FITS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SUBMIT FITS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

exp_opts = '--expectSignal 1 -t -1'
common_opts = '--cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2'
#job_opts = '--job-mode SGE --sub-opts "-q hep.q -l h_rt=3:0:0 -l h_vmem=24G -pe hep.pe 2"'
job_opts = '--job-mode condor --sub-opts=\'+JobFlavour = \"workday\"\''

def getPdfIndicesFromJson(pdfjson):
  pdfStr = "--setParameters "
  with open(pdfjson) as jsonfile: pdfidxs = json.load(jsonfile)
  for k,v in pdfidxs.iteritems(): pdfStr += "%s=%s,"%(k,v)
  return pdfStr[:-1]

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Type of fit")
  parser.add_option('--ext', dest='ext', default='', help="In case running over Datacard with extension")
  parser.add_option('--setPdfIndices', dest='setPdfIndices', action="store_true", default=False, help="Set pdf indixes from pdfindex.json")
  parser.add_option('--doObserved', dest='doObserved', action="store_true", default=False, help="Fit to data")
  parser.add_option('--snapshotWSFile', dest='snapshotWSFile', default='', help="Full path to snapshot WS file")
  parser.add_option('--dryRun', dest='dryRun', action="store_true", default=False, help="Only create submission files")
  return parser.parse_args()
(opt,args) = get_options()

# If observed
if opt.doObserved: exp_opts = ''

# Make folder for running fits if does not exist
if not os.path.isdir("runFits%s_%s"%(opt.ext,opt.mode)): os.system("mkdir runFits%s_%s"%(opt.ext,opt.mode))

# Read json file
with open( opt.inputJson ) as jsonfile: inputs = json.load(jsonfile)[opt.mode]

# Extract info
pois = inputs['pois'].split(",")
fits = inputs['fits'].split("+")
points = inputs['points'].split("+")
fit_opts = inputs['fit_opts'].split("+")

# Loop over fits and set running
for fidx in range(len(fits)):
  _fit = fits[fidx]
  if _fit.split(":")[2] == "all": _fitpois = pois
  else: _fitpois = _fit.split(":")[2].split(",")

  _points = points[fidx]
  _fit_opts = fit_opts[fidx]
  if opt.dryRun: _fit_opts += " --dry-run"
  _name = "%s_%s"%(_fit.split(":")[0],_fit.split(":")[1])
  if opt.doObserved: _name += "_obs"
  pdf_opts = getPdfIndicesFromJson("pdfindex%s.json"%opt.ext) if opt.setPdfIndices else ''
  # File to load workspace
  if opt.snapshotWSFile != '': d_opts = '-d %s --snapshotName MultiDimFit'%opt.snapshotWSFile
  else: d_opts = '-d ../Datacard%s_%s.root'%(opt.ext,opt.mode)

  # For best fit point
  if _fit.split(":")[0] == "bestfit":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s -P %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For singles point
  if _fit.split(":")[0] == "singles":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s -P %s --algo singles %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For 1D scan when profiling other pois
  elif _fit.split(":")[0] == "profile1D":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s -P %s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For 1D scan when fixing other pois
  elif _fit.split(":")[0] == "scan1D":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 0 %s -n _%s_%s -P %s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For 2D scan: fix other pois to 0
  elif _fit.split(":")[0] == "profile2D":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    _poisStr = "%s_vs_%s"%(_fitpois[0],_fitpois[1])
    fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s -P %s -P %s --floatOtherPOIs 1 %s -n _%s_%s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,_poisStr,d_opts,_fitpois[0],_fitpois[1],exp_opts,_name,_poisStr,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)
    run(fitcmd)

  # For 2D scan: fix other pois to 0
  elif _fit.split(":")[0] == "scan2D":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    _poisStr = "%s_vs_%s"%(_fitpois[0],_fitpois[1])
    fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s -P %s -P %s --floatOtherPOIs 0 %s -n _%s_%s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,_poisStr,d_opts,_fitpois[0],_fitpois[1],exp_opts,_name,_poisStr,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)    
    run(fitcmd)

  # Robust Hesse
  elif _fit.split(":")[0] == "robustHesse":
    if "statonly" in _fit.split(":")[1]: _fit_opts += " --freezeParameters allConstrainedNuisances"
    _poi = _fitpois[0]
    fitcmd = "cd runFits%s_%s; combineTool.py --task-name %s -M MultiDimFit -m 125 %s -P %s --floatOtherPOIs 1 %s -n _%s --robustHesse 1 --robustHesseSave 1 --saveFitResult %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,d_opts,_poi,exp_opts,_name,_fit_opts,pdf_opts,common_opts,job_opts)
    run(fitcmd)
