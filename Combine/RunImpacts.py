# Script to submit fit jobs
import ROOT
import os, sys
import re
from optparse import OptionParser
import glob
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SUBMIT IMPACTS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "

# subOpts for SGE e.g.: -l h_rt=3:0:0 -l h_vmem=24G -pe hep.pe 2

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Type of fit")
  parser.add_option('--ext', dest='ext', default='', help="Running over Datacard with extension")
  parser.add_option('--setPdfIndices', dest='setPdfIndices', action="store_true", default=False, help="Set pdf indixes from pdfindex.json")
  parser.add_option('--doObserved', dest='doObserved', action="store_true", default=False, help="Fit to data")
  parser.add_option('--doFits', dest='doFits', action="store_true", default=False, help="run one scan per nuisance parameter. Needs initialFit to have been run earlier.")
  parser.add_option('--commonOpts', dest='commonOpts', default="--cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2", help="Common combine options for running fits")
  parser.add_option('--batch', dest='batch', default='condor', help='Batch: [crab,condor/SGE/IC/lxbatch]')
  parser.add_option('--queue', dest='queue', default='espresso', help='Queue e.g. for condor=workday, for IC=hep.q')
  parser.add_option('--subOpts', dest='subOpts', default="", help="Submission options")
  parser.add_option('--dryRun', dest='dryRun', action="store_true", default=False, help="Only create submission files")
  return parser.parse_args()
(opt,args) = get_options()

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SUBMIT IMPACTS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  exit(1)

def run(cmd,opt):
  if opt.dryRun:
    print "%s\n\n"%cmd
  else:
    os.system(cmd)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Options:
# Expected/Observed
exp_opts = '' if opt.doObserved else '-t -1'

# Common opts for combine jobs
common_opts = opt.commonOpts

# Extract path to WS file


# Options for job submission
if opt.batch == 'condor': 
  sub_opts = "--sub-opts=\'+JobFlavour = \"%s\""%opt.queue
  if opt.subOpts != "": sub_opts += "\n%s"%opt.subOpts
  sub_opts += "\'"
  job_opts = "--job-mode condor %s"%sub_opts
elif( opt.batch == 'SGE' )|( opt.batch == 'IC' )|( opt.batch == 'lxbatch' ):
  sub_opts = "--sub-opts=\'-q %s"%opt.queue
  if opt.subOpts != "": sub_opts += " %s"%opt.subOpts
  sub_opts += "\'"
  job_opts = "--job-mode %s %s"%(opt.batch,sub_opts)
elif opt.batch == "local":
  print "--> Will print the commands to run combine without combineTool interactively\n\n"
else:
  print " --> [ERROR] Batch mode (%s) not supported. Leaving"%opt.batch
  leave()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Make folder for running fits if does not exist
if not os.path.isdir("runImpacts%s_%s"%(opt.ext,opt.mode)): os.system("mkdir runImpacts%s_%s"%(opt.ext,opt.mode))

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
  # robustFit is needed, so it is enforced below. Do not repeat twice in case it is given.
  _fit_opts = fit_opts[fidx].replace("--robustFit=1","").replace("--robustFit 1","")
  # in case of doFits, combineTool adds floatOtherPOIs 1, so do not repeat twice in case it is given
  if opt.doFits:
    _fit_opts = _fit_opts.replace("--floatOtherPOIs=1","").replace("--floatOtherPOIs 1","")
    _fit_opts = _fit_opts.replace("--saveInactivePOI=1","").replace("--saveInactivePOI 1","")
    _fit_opts = _fit_opts.replace("--saveWorkspace","")

  # If ALL in fit_opts: replace by list of constrained nuisances in workspace
  if "ALL" in _fit_opts: 
    fd = ROOT.TFile("Datacard_%s.root"%(opt.ext))
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

  # add this to distinguish different fits with same POI
  _name += "_"+opt.ext

  d_opts = '-d %s/src/flashggFinalFit/Combine/Datacard_%s.root'%(os.environ['CMSSW_BASE'],opt.ext)

  # If setParameters already in _fit_opts then add to fit opts and set pdfOpts = ''
  if( "setParameters" in _fit_opts )&( pdf_opts != '' ):
    pdfstr = re.sub("--setParameters ","",pdf_opts)
    _fit_opts = re.sub("--setParameters ","--setParameters %s,"%pdfstr,_fit_opts)
    pdf_opts = ''

  # Running different types of fits...

  # For best fit point
  if _fit.split(":")[0] == "bestfit":
    if( "statonly" in _fit.split(":")[1] )&( "freezeParameters" not in _fit_opts ): _fit_opts += " --freezeParameters allConstrainedNuisances"
    impactcmd1 = "cd runImpacts%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_initialFit -M Impacts -m 125.38 %s %s --doInitialFit --robustFit 1 -n _%s_initialFit %s %s %s"%(opt.ext,opt.mode,_name,d_opts,exp_opts,_name,_fit_opts,pdf_opts,common_opts)
    impactcmd2 = "cd runImpacts%s_%s; source /cvmfs/cms.cern.ch/crab3/crab.sh; combineTool.py --task-name %s_doFits -M Impacts -m 125.38 %s %s --doFits -n _%s_initialFit %s %s %s"%(opt.ext,opt.mode,_name,d_opts,exp_opts,_name,_fit_opts,pdf_opts,common_opts)
    if opt.batch != 'local':
      impactcmd1 += " %s"%job_opts
      impactcmd2 += " %s"%job_opts
    if not opt.doFits:
      run(impactcmd1,opt) 
    else:
      print(impactcmd2)
      run(impactcmd2,opt)
