import os
import glob
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDir',dest='inputDir', default="", help='Input path to workspace directories')
  parser.add_option('--outputDir',dest='outputDir', default="", help='Output path')
  parser.add_option('--fggBase',dest='fggBase', default="/vols/build/cms/jl2117/hgg/FinalFits/legacy/Feb20_unblinding/old_bkg/CMSSW_10_6_8/src", help='flashgg base')
  parser.add_option('--year',dest='year', default="2016", help='Year')
  parser.add_option('--ext',dest='ext', default="", help='Extension')
  parser.add_option('--doSplit',dest='doSplit', default=False, action="store_true", help='Do split')
  return parser.parse_args()
(opt,args) = get_options()

if not os.path.isdir("./hadd_jobs_%s%s"%(opt.year,opt.ext)): os.system("mkdir ./hadd_jobs_%s%s"%(opt.year,opt.ext))
wsFolders = glob.glob("%s/ws_*"%opt.inputDir)
for wsFidx in range(len(wsFolders)):
  wsF = wsFolders[wsFidx]
  # Extract name of input 
  # Extract processes
  proc = "_".join(wsF.split("ws_")[-1].split("_")[1:])
  if(opt.doSplit)&( "_".join(proc.split("_")[:-1]) == "TH" ): splitidx = "_%s"%proc.split("_")[-1]
  else: splitidx = ""
  # Define output file name
  outF = "_".join(glob.glob("%s/output_*"%wsF)[0].split("/")[-1].split("_")[:-1])+"%s.root"%splitidx
  outFileName = "%s/%s"%(opt.outputDir,outF)
  # Open submission file to write to
  fsub = open("./hadd_jobs_%s%s/sub%g.sh"%(opt.year,opt.ext,wsFidx),'w')  
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd %s\n\n"%opt.fggBase)
  fsub.write("eval `scramv1 runtime -sh`\n\n")
  fsub.write("hadd_workspaces %s %s/output_*"%(outFileName,wsF))
  fsub.close()

os.system("chmod 775 ./hadd_jobs_%s%s/sub*.sh"%(opt.year,opt.ext))
