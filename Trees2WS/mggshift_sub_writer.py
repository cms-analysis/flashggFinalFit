import os
import glob
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDir',dest='inputDir', default="", help='Input path to workspaces')
  parser.add_option('--inputMass',dest='inputMass', default="125", help='Input mass')
  parser.add_option('--targetMasses',dest='targetMasses', default="120,130", help='Target masses')
  parser.add_option('--year',dest='year', default="2016", help='Year')
  parser.add_option('--ext',dest='ext', default="", help='Extension')
  return parser.parse_args()
(opt,args) = get_options()

if not os.path.isdir("./mggshift_jobs_%s%s"%(opt.year,opt.ext)): os.system("mkdir ./mggshift_jobs_%s%s"%(opt.year,opt.ext))
wsFiles = glob.glob("%s/output_*"%opt.inputDir)
for wsidx in range(len(wsFiles)):
  ws = wsFiles[wsidx]
  # Open submission file to write to
  fsub = open("./mggshift_jobs_%s%s/sub%g.sh"%(opt.year,opt.ext,wsidx),'w')  
  fsub.write("#!/bin/bash\n\n")
  fsub.write("cd %s\n\n"%os.environ['PWD'])
  fsub.write("eval `scramv1 runtime -sh`\n\n")
  for targetMass in opt.targetMasses.split(","):
    fsub.write("python mgg_shifter.py --inputFile %s --inputMass %s --targetMass %s\n"%(ws,opt.inputMass,targetMass))
  fsub.close()

os.system("chmod 775 ./mggshift_jobs_%s%s/sub*.sh"%(opt.year,opt.ext))
