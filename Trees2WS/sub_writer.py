import glob
import sys, os

#ext = "_multiclassifier"
ext = ""
year = "2016"
script = "pandas2ws.py"
scriptShortcut = {"trees2pandas.py":"t2p", "pandas2ws.py":"p2w", "trees2ws_data.py":"t2wd"}
if not os.path.isdir("./%s_jobs_%s%s"%(scriptShortcut[script],year,ext)): os.system("mkdir ./%s_jobs_%s%s/"%(scriptShortcut[script],year,ext))

if script == "trees2pandas.py": inputFileNames = glob.glob("/vols/cms/jl2117/hgg/ws/April20/trees/MC%s/%s/output_*"%(ext,year))
elif script == "pandas2ws.py": inputFileNames = glob.glob("/vols/cms/jl2117/hgg/ws/April20/trees/MC%s/%s/pickle_*/*"%(ext,year))
elif script == "trees2ws_data.py": 
  inputFileNames = glob.glob("/vols/cms/es811/HggGeneral/WorkspaceTest/Pass5/MultiClass/%s/Data/Raw/output_*"%year)
  outputWSPath = "/vols/cms/jl2117/hgg/ws/April20/ws/data%s/%s"%(ext,year)

for i in range(len(inputFileNames)):
  fin = inputFileNames[i]
  
  # Open submission file to write to
  fsub = open("./%s_jobs_%s%s/sub%g.sh"%(scriptShortcut[script],year,ext,i),'w')
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/April20/CMSSW_10_2_13/src/flashggFinalFit/Trees2WS\n\n")
  fsub.write("eval `scramv1 runtime -sh`\n\n")

  # Extract production mode
  if script == "trees2ws_data.py": p = "data"
  elif "GluGlu" in fin: p = "ggh"
  elif "VBF" in fin: p = "vbf"
  elif "WH" in fin: p = "wh"
  elif "ZH" in fin: p = "zh"
  elif "ttH" in fin: p = "tth"
  elif "THQ" in fin: p = "thq"
  else: 
    print "ERROR: invalid input file, cannot find production mode"
    sys.exit(1)

  if script == "trees2pandas.py":
    fsub.write("python %s --inputTreeFile %s --productionMode %s --year %s\n"%(script,fin,p,year))
  elif script == "pandas2ws.py":
    fsub.write("python %s --inputPandasFile %s --productionMode %s --year %s\n"%(script,fin,p,year))
  elif script == "trees2ws_data.py":
    fsub.write("python %s --inputTreeFile %s --outputWSPath %s\n"%(script,fin,outputWSPath))
  else:
    print "ERROR: invalid script: %s"%script

  fsub.close()

os.system("chmod 775 ./%s_jobs_%s%s/sub*.sh"%(scriptShortcut[script],year,ext))
