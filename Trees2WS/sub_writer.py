import glob
import sys, os
from optparse import OptionParser

scriptShortcut = {"trees2pandas.py":"t2p", "pandas2ws.py":"p2w", "trees2ws_data.py":"t2wd"}

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDir',dest='inputDir', default="", help='Input path to tree directory')
  parser.add_option('--outputDir',dest='outputDir', default="~", help='Used only for trees2ws_data.py script')
  parser.add_option('--script',dest='script', default = '', help="Options: trees2pandas.py, pandas2ws.py, trees2ws_data.py")
  parser.add_option('--year',dest='year', default="2016", help='Year')
  parser.add_option('--ext',dest='ext', default="", help='Extension')
  return parser.parse_args()
(opt,args) = get_options()

if opt.script not in ['trees2pandas.py', 'pandas2ws.py', 'trees2ws_data.py']: 
  print " --> [ERROR] Script %s not recognized. Please use: trees2pandas.py, pandas2ws.py, trees2ws_data.py"
  sys.exit(1)

# Make directory for submission jobs
if not os.path.isdir("./%s_jobs_%s%s"%(scriptShortcut[opt.script],opt.year,opt.ext)): os.system("mkdir ./%s_jobs_%s%s/"%(scriptShortcut[opt.script],opt.year,opt.ext))

# Extract input file names
if opt.script == "trees2pandas.py": inputFileNames = glob.glob("%s/output_*"%opt.inputDir)
elif opt.script == "pandas2ws.py": inputFileNames = glob.glob("%s/pickle_*/*"%opt.inputDir)
elif opt.script == "trees2ws_data.py": 
  inputFileNames = glob.glob("%s/output_*"%opt.inputDir)
  outputWSPath = opt.outputDir

for i in range(len(inputFileNames)):
  fin = inputFileNames[i]
  
  # Open submission file to write to
  fsub = open("./%s_jobs_%s%s/sub%g.sh"%(scriptShortcut[opt.script],opt.year,opt.ext,i),'w')
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/April20/CMSSW_10_2_13/src/flashggFinalFit/Trees2WS\n\n")
  fsub.write("eval `scramv1 runtime -sh`\n\n")

  # Extract production mode (and decay if needed e.g. for ggzh)
  p, d = "", ""
  if opt.script == "trees2ws_data.py": p = "data"
  elif "ggZH" in fin:
    p = "ggzh"
    if "ZToLL" in fin: d = "_ZToLL"
    elif "GG2HLL" in fin: d = "_ZToLL"
    elif "ZToNuNu" in fin: d = "_ZToNuNu"
    elif "GG2HNUNU" in fin: d = "_ZToNuNu"
    else: d = "_ZToQQ"
  elif "GluGlu" in fin: p = "ggh"
  elif "VBF" in fin: p = "vbf"
  elif "WH" in fin: p = "wh"
  elif "ZH" in fin: p = "zh"
  elif "ttH" in fin: p = "tth"
  elif "THQ" in fin: p = "thq"
  elif "bbH" in fin: p = "bbh"
  else: 
    print "ERROR: invalid input file, cannot find production mode"
    sys.exit(1)

  if opt.script == "trees2pandas.py":
    if d == '': fsub.write("python %s --inputTreeFile %s --productionMode %s --year %s\n"%(opt.script,fin,p,opt.year))
    else: fsub.write("python %s --inputTreeFile %s --productionMode %s --year %s --decayExt %s\n"%(opt.script,fin,p,opt.year,d))
  elif opt.script == "pandas2ws.py":
    if d == '': fsub.write("python %s --inputPandasFile %s --productionMode %s --year %s\n"%(opt.script,fin,p,opt.year))
    else: fsub.write("python %s --inputPandasFile %s --productionMode %s --year %s --decayExt %s\n"%(opt.script,fin,p,opt.year,d))
  elif opt.script == "trees2ws_data.py":
    fsub.write("python %s --inputTreeFile %s --outputWSPath %s\n"%(opt.script,fin,outputWSPath))
  else:
    print "ERROR: invalid script: %s"%opt.script

  fsub.close()

os.system("chmod 775 ./%s_jobs_%s%s/sub*.sh"%(scriptShortcut[opt.script],opt.year,opt.ext))
