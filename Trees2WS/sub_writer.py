import glob
import sys, os

year = "2017"
script = "pandas2ws.py"
scriptShortcut = {"trees2pandas.py":"t2p", "pandas2ws.py":"p2w"}

if script == "trees2pandas.py": inputFileNames = glob.glob("/vols/cms/jl2117/hgg/ws/Feb20/trees/%s/output_*"%year)
elif script == "pandas2ws.py": inputFileNames = glob.glob("/vols/cms/jl2117/hgg/ws/Feb20/trees/%s/pickle_*/*"%year)

for i in range(len(inputFileNames)):
  fin = inputFileNames[i]
  
  # Open submission file to write to
  fsub = open("./%s_jobs_%s/sub%g.sh"%(scriptShortcut[script],year,i),'w')
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/feb20_stage1_2/CMSSW_10_2_13/src/flashggFinalFit/Trees2WS\n\n")
  fsub.write("eval `scramv1 runtime -sh`\n\n")

  # Extract production mode
  if "GluGlu" in fin: p = "ggh"
  elif "VBF" in fin: p = "vbf"
  elif "WH" in fin: p = "wh"
  elif "ZH" in fin: p = "zh"
  elif "ttH" in fin: p = "tth"
  elif "THQ" in fin: p = "thq"
  else: 
    print "ERROR: invalid input file, cannot find production mode"
    sys.exit(1)

  if script == "trees2pandas.py":
    fsub.write("python %s --inputTreeFile %s --productionMode %s\n"%(script,fin,p))
  elif script == "pandas2ws.py":
    fsub.write("python %s --inputPandasFile %s --productionMode %s\n"%(script,fin,p))
  else:
    print "ERROR: invalid script: %s"%script

  fsub.close()

os.system("chmod 775 ./%s_jobs_%s/sub*.sh"%(scriptShortcut[script],year))
