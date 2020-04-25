# Script to make toys from inputWS: to be used for making bands in S+B model plot

import os, sys
import re
from optparse import OptionParser
import ROOT
import glob

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--nToys", dest="nToys", default=500, type='int', help="Number of toys")
  parser.add_option("--POI", dest="POI", default="r", help="Parameter of interest in fit")
  parser.add_option('--dryRun',dest='dryRun', default=False, action="store_true", help='Dry run')
  return parser.parse_args()
(opt,args) = get_options()

# Create jobs directory
if not os.path.isdir("./SplusBModels%s"%(opt.ext)): os.system("mkdir ./SplusBModels%s"%(opt.ext))
if not os.path.isdir("./SplusBModels%s/toys"%(opt.ext)): os.system("mkdir ./SplusBModels%s/toys"%(opt.ext))
if not os.path.isdir("./SplusBModels%s/toys/jobs"%(opt.ext)): os.system("mkdir ./SplusBModels%s/toys/jobs"%(opt.ext))

# Delete all old jobs
for job in glob.glob("./SplusBModels%s/toys/jobs/sub*.sh"%opt.ext): os.system("rm %s"%job)

# Open workspace and extract best fit mass and signal strength
inputWSFile = "%s/%s"%(os.environ['PWD'],opt.inputWSFile)
f = ROOT.TFile(inputWSFile)
w = f.Get("w")
if opt.loadSnapshot is not None: w.loadSnapshot(opt.loadSnapshot)
poi_bf = w.var( opt.POI ).getVal()
mh_bf = w.var("MH").getVal()

# Create submission file
for itoy in range(0,opt.nToys):
  fsub = open("./SplusBModels%s/toys/jobs/sub_toy_%g.sh"%(opt.ext,itoy),'w')
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd %s/src/flashggFinalFit/Plots/SplusBModels%s/toys\n\n"%(os.environ['CMSSW_BASE'],opt.ext))
  fsub.write("eval `scramv1 runtime -sh`\n\n")
  # Generate command
  fsub.write("#Generate command\n")
  #gen_cmd = "combine %s -m %.3f -M GenerateOnly --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --setParameters %s=%.3f -s -1 -n _%g_gen_step"%(inputWSFile,mh_bf,opt.POI,poi_bf,itoy)
  gen_cmd = "combine %s -m %.3f -M GenerateOnly --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal %.3f -s -1 -n _%g_gen_step"%(inputWSFile,mh_bf,poi_bf,itoy)
  if opt.loadSnapshot is not None: gen_cmd += " --snapshotName %s"%opt.loadSnapshot
  fsub.write("%s\n\n"%gen_cmd)
  # Fit cmd
  fsub.write("#Fit command\n")
  fsub.write("mv higgsCombine_%g_gen_step*.root gen_%g.root\n"%(itoy,itoy))
  #fit_cmd = "combine gen_%g.root -m %.3f -M MultiDimFit --floatOtherPOIs=1 --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --setParameters %s=%.3f -s -1 -n _%g_fit_step --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(itoy,mh_bf,opt.POI,poi_bf,itoy)
  fit_cmd = "combine gen_%g.root -m %.3f -M MultiDimFit --floatOtherPOIs=1 --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal %.3f -s -1 -n _%g_fit_step --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(itoy,mh_bf,poi_bf,itoy)
  fsub.write("%s\n\n"%fit_cmd)
  # Throw cmd
  fsub.write("#Throw command\n")
  fsub.write("mv higgsCombine_%g_fit_step*.root fit_%g.root\n"%(itoy,itoy))
  throw_cmd = "combine fit_%g.root -m %.3f --snapshotName MultiDimFit -M GenerateOnly --saveToys --toysFrequentist --bypassFrequentistFit -t -1 -n _%g_throw_step --expectSignal 0"%(itoy,mh_bf,itoy)
  fsub.write("%s\n\n"%throw_cmd)
  # Clean up
  fsub.write("mv higgsCombine_%g_throw_step*.root toy_%g.root\n"%(itoy,itoy))
  #fsub.write("rm gen_%g.root fit_%g.root\n"%(itoy,itoy))
  fsub.close()

# Change permission of all files and set running on batch
os.system("chmod 775 ./SplusBModels%s/toys/jobs/sub*.sh"%opt.ext)
if not opt.dryRun:
  subs = glob.glob("./SplusBModels%s/toys/jobs/sub*"%opt.ext)
  for fsub in subs: os.system("qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G %s"%fsub)
else: print " --> [DRY-RUN] jobs have not been submitted"
  
