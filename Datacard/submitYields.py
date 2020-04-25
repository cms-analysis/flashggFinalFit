import os, sys
import glob
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputWSDir', dest='inputWSDir', default='/vols/cms/jl2117/hgg/ws/test_stage1_1', help='Input WS directory (without year tag _201X)')
  parser.add_option('--cats', dest='cats', default='', help='Analysis categories')
  parser.add_option('--doNoTag', dest='doNoTag', default=False, action="store_true", help='Process yields for NO TAG')
  parser.add_option('--years', dest='years', default='2016', help="Comma separated list of years")
  parser.add_option('--modelWSDir', dest='modelWSDir', default='Models', help='Input model WS directory')
  parser.add_option('--ext', dest='ext', default='', help='Extension for saving')
  parser.add_option('--bkgScaler', dest='bkgScaler', default=1., type="float", help="Add overall scale factor for background")
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option('--doBkgSplit', dest='doBkgSplit', default=False, action="store_true", help="Split background models to different files (is used fTestParallel)")
  parser.add_option('--skipBkg', dest='skipBkg', default=False, action="store_true", help="Only add signal processes to datacard")
  parser.add_option('--skipCOWCorr', dest='skipCOWCorr', default=False, action="store_true", help="Skip centralObjectWeight correction for events in acceptance")
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--packagedSignal', dest='packagedSignal', default=False, action="store_true", help='Signal models packaged into one file per category')
  parser.add_option('--dryRun', dest='dryRun', default=False, action="store_true", help='Dry run: do not submit scripts to batch')
  return parser.parse_args()
(opt,args) = get_options()

# Construct command line
cmdLine = "python makeYields.py --inputWSDir %s --years %s --modelWSDir %s"%(opt.inputWSDir,opt.years,opt.modelWSDir)
if opt.ext != '': cmdLine += " --ext %s"%opt.ext
if opt.bkgScaler != 1.: cmdLine += " --bkgScaler %.7f"%opt.bkgScaler
if opt.mergeYears: cmdLine += " --mergeYears"
if opt.doBkgSplit: cmdLine += " --doBkgSplit"
if opt.skipBkg: cmdLine += " --skipBkg"
if opt.skipCOWCorr: cmdLine += " --skipCOWCorr"
if opt.doSystematics: cmdLine += " --doSystematics"
if opt.packagedSignal: cmdLine += " --packagedSignal"

# Create directory for submission scripts
if not os.path.isdir("./yields%s"%opt.ext): os.system("mkdir ./yields%s"%opt.ext)
if not os.path.isdir("./yields%s/jobs"%opt.ext): os.system("mkdir ./yields%s/jobs"%opt.ext)

# Create submission script for each category
if opt.doNoTag: cats = opt.cats + ",NOTAG"
else: cats = opt.cats
for cat in cats.split(","):
  fsub = open("./yields%s/jobs/sub_%s.sh"%(opt.ext,cat),"w")
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd %s/src/flashggFinalFit/Datacard\n\n"%os.environ['CMSSW_BASE'])
  fsub.write("eval `scramv1 runtime -sh`\n\n")
  fsub.write("%s --cat %s"%(cmdLine,cat))
  fsub.close()

# Change permission for scripts
os.system("chmod 775 ./yields%s/jobs/sub_*.sh"%opt.ext)

print " --> Submission scripts written: ./yields%s/jobs/sub_{cat}.sh"%opt.ext

if not opt.dryRun:
  subs = glob.glob("yields%s/jobs/sub*"%opt.ext)
  for fsub in subs: os.system("qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G %s"%fsub) 
else: print " --> [DRY-RUN] jobs have not been submitted"
