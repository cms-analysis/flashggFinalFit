# Script to submit fit jobs
import ROOT
import os, sys
import re
from optparse import OptionParser
import glob
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SUBMIT FITS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "

# subOpts for SGE e.g.: -l h_rt=3:0:0 -l h_vmem=24G -pe hep.pe 2

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Type of fit")
  parser.add_option('--ext', dest='ext', default='', help="Running over Datacard with extension")
  parser.add_option('--setPdfIndices', dest='setPdfIndices', action="store_true", default=False, help="Set pdf indixes from pdfindex.json")
  parser.add_option('--doObserved', dest='doObserved', action="store_true", default=False, help="Fit to data")
  parser.add_option('--snapshotWSFile', dest='snapshotWSFile', default='', help="Full path to snapshot WS file (use when running observed statonly as nuisances are froze at postfit values)")
  parser.add_option('--commonOpts', dest='commonOpts', default="--cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2", help="Common combine options for running fits")
  parser.add_option('--batch', dest='batch', default='condor', help='Batch: [crab,condor/SGE/IC]')
  parser.add_option('--queue', dest='queue', default='workday', help='Queue e.g. for condor=workday, for IC=hep.q')
  parser.add_option('--subOpts', dest='subOpts', default="", help="Submission options")
  parser.add_option('--doCustomCrab', dest='doCustomCrab', default=False, action="store_true", help="Load crab options from custom_crab.py file")
  parser.add_option('--crabMemory', dest='crabMemory', default='5900', help="Memory for crab job")
  parser.add_option('--dryRun', dest='dryRun', action="store_true", default=False, help="Only create submission files")
  return parser.parse_args()
(opt,args) = get_options()

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SUBMIT FITS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  exit(1)

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def getPdfIndicesFromJson(pdfjson):
  pdfStr = "--setParameters "
  with open(pdfjson) as jsonfile: pdfidxs = json.load(jsonfile)
  for k,v in pdfidxs.iteritems(): pdfStr += "%s=%s,"%(k,v)
  return pdfStr[:-1]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Options:
# Expected/Observed
exp_opts = '' if opt.doObserved else '--expectSignal 1 -t -1'

# Common opts for combine jobs
common_opts = opt.commonOpts

# Extract path to WS file


# Options for job submission
if opt.batch == 'crab':
  job_opts = "--job-mode crab3"
  if opt.doCustomCrab: job_opts += " --custom-crab %s/src/flashggFinalFit/Combine/custom_crab.py"%os.environ['CMSSW_BASE']
  job_opts += " --memory %s"%opt.crabMemory
elif opt.batch == 'condor': 
  sub_opts = "--sub-opts=\'+JobFlavour = \"%s\""%opt.queue
  if opt.subOpts != "": sub_opts += "\n%s"%opt.subOpts
  sub_opts += "\'"
  job_opts = "--job-mode condor %s"%sub_opts
elif( opt.batch == 'SGE' )|( opt.batch == 'IC' ):
  sub_opts = "--sub-opts=\'-q %s"%opt.queue
  if opt.subOpts != "": sub_opts += " %s"%opt.subOpts
  sub_opts += "\'"
  job_opts = "--job-mode SGE %s"%sub_opts
else:
  print " --> [ERROR] Batch mode (%s) not supported. Leaving"%opt.batch
  leave()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

  # If ALL in fit_opts: replace by list of constrained nuisances in workspace
  if "ALL" in _fit_opts: 
    fd = ROOT.TFile("Datacard%s_%s.root"%(opt.ext,opt.mode))
    ws = fd.Get("w")
    nuisances = ws.obj("ModelConfig").GetNuisanceParameters().contentsString()
    _fit_opts = re.sub("ALL",nuisances,_fit_opts)
    ws.Delete()
    fd.Close()

  # Dry run
  if opt.dryRun: _fit_opts += " --dry-run"
  _name = "%s_%s"%(_fit.split(":")[0],_fit.split(":")[1])

  # Setting PDF indices
  if opt.doObserved: 
    _name += "_obs"
    pdf_opts = getPdfIndicesFromJson("pdfindex%s_observed.json"%opt.ext) if opt.setPdfIndices else ''
  else: pdf_opts = getPdfIndicesFromJson("pdfindex%s.json"%opt.ext) if opt.setPdfIndices else ''

  # File to load workspace
  if opt.snapshotWSFile != '': d_opts = '-d %s --snapshotName MultiDimFit'%opt.snapshotWSFile
  else:
    #d_opts = '-d ../Datacard%s_%s.root'%(opt.ext,opt.mode)
    d_opts = '-d %s/src/flashggFinalFit/Combine/Datacard%s_%s.root'%(os.environ['CMSSW_BASE'],opt.ext,opt.mode)

  # If setParameters already in _fit_opts then add to fit opts and set pdfOpts = ''
  if( "setParameters" in _fit_opts )&( pdf_opts != '' ):
    pdfstr = re.sub("--setParameters ","",pdf_opts)
    _fit_opts = re.sub("--setParameters ","--setParameters %s,"%pdfstr,_fit_opts)
    pdf_opts = ''

  # Running different types of fits...

  # For best fit point
  if _fit.split(":")[0] == "bestfit":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s -P %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For singles point
  if _fit.split(":")[0] == "singles":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s -P %s --algo singles %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For fixed point
  if _fit.split(":")[0] == "fixed":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s --algo fixed %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For asymptotic limit
  if _fit.split(":")[0] == "AsymptoticLimit":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M AsymptoticLimits -m 125 %s %s -n _%s_%s --redefineSignalPOI %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For 1D scan when profiling other pois
  elif _fit.split(":")[0] == "profile1D":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 1 %s -n _%s_%s -P %s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For 1D scan when fixing other pois
  elif _fit.split(":")[0] == "scan1D":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    for poi in _fitpois:
      fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s --floatOtherPOIs 0 %s -n _%s_%s -P %s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,poi,d_opts,exp_opts,_name,poi,poi,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)
      run(fitcmd)

  # For 2D scan: fix other pois to 0
  elif _fit.split(":")[0] == "profile2D":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    _poisStr = "%s_vs_%s"%(_fitpois[0],_fitpois[1])
    fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s -P %s -P %s --floatOtherPOIs 1 %s -n _%s_%s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,_poisStr,d_opts,_fitpois[0],_fitpois[1],exp_opts,_name,_poisStr,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)
    run(fitcmd)

  # For 2D scan: fix other pois to 0
  elif _fit.split(":")[0] == "scan2D":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    _poisStr = "%s_vs_%s"%(_fitpois[0],_fitpois[1])
    fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_%s -M MultiDimFit -m 125 %s -P %s -P %s --floatOtherPOIs 0 %s -n _%s_%s --algo grid --points %s --alignEdges 1 --split-points %s %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,_poisStr,d_opts,_fitpois[0],_fitpois[1],exp_opts,_name,_poisStr,_points.split(":")[0],_points.split(":")[1],_fit_opts,pdf_opts,common_opts,job_opts)    
    run(fitcmd)

  # Robust Hesse
  elif _fit.split(":")[0] == "robustHesse":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    _poi = _fitpois[0]
    fitcmd = "cd runFits%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s -M MultiDimFit -m 125 %s -P %s --floatOtherPOIs 1 %s -n _%s --robustHesse 1 --robustHesseSave 1 --saveFitResult %s %s %s %s; cd .."%(opt.ext,opt.mode,_name,d_opts,_poi,exp_opts,_name,_fit_opts,pdf_opts,common_opts,job_opts)
    run(fitcmd)
