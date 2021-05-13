import os, re, glob
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputTreeDir',dest='inputTreeDir', default="", help="Input path to nominal trees")
  parser.add_option('--year',dest='year',default="2016", help="Year")
  parser.add_option('--mode',dest='mode',default="nominal", help="Looping over nominal trees or UEPS trees")
  parser.add_option('--dryRun',dest='dryRun',default=False, action="store_true", help="Dry run")
  return parser.parse_args()
(opt,args) = get_options()

# Extract tree files
fileNames = glob.glob("%s/output*.root"%opt.inputTreeDir)

# Create submission file for each
if not os.path.isdir("ueps_dataframes_%s"%opt.year): os.system("mkdir ueps_dataframes_%s"%opt.year)
if not os.path.isdir("ueps_dataframes_%s/jobs_%s"%(opt.year,opt.mode)): os.system("mkdir ueps_dataframes_%s/jobs_%s"%(opt.year,opt.mode))
for fidx in range(len(fileNames)):
  fname = fileNames[fidx]
  fw = open("ueps_dataframes_%s/jobs_%s/sub_%g.sh"%(opt.year,opt.mode,fidx),"w")
  fw.write("#!/bin/bash\n\n")
  fw.write("cd %s/src/flashggFinalFit/Datacard\n\n"%os.environ['CMSSW_BASE'])
  fw.write("eval `scramv1 runtime -sh`\n\n")
  fw.write("export PYTHONPATH=${PYTHONPATH}:%s/src/flashggFinalFit/tools\n\n"%os.environ['CMSSW_BASE'])
  fw.write("python extractUEPS.py --inputTreeFile %s --year %s --mode %s --ext _%s_%s\n\n"%(fname,opt.year,opt.mode,opt.mode,fidx))
  fw.close()

# Change permission on files
os.system("chmod 775 ueps_dataframes_%s/jobs_%s/sub*.sh"%(opt.year,opt.mode))

# Submit if not dryRun
if not opt.dryRun:
  for fidx in range(len(fileNames)): os.system("qsub -q hep.q -l h_rt=0:20:0 -l h_vmem=24G ueps_dataframes_%s/jobs_%s/sub_%g.sh"%(opt.year,opt.mode,fidx))
  
