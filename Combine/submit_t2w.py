import os, glob
from optparse import OptionParser
from models import models

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG T2W RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG T2W RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def get_options():
  parser = OptionParser()
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Physics Model")
  parser.add_option('--ext',dest='ext', default="", help='In case running over datacard with extension')
  parser.add_option('--common_opts',dest='common_opts', default="-m 125 higgsMassRange=122,128", help='Common options')
  parser.add_option('--dryRun', dest='dryRun', action="store_true", default=False, help="Only create submission files")
  return parser.parse_args()
(opt,args) = get_options()

if opt.mode not in models: 
  print " --> [ERROR] opt.mode (%s) is not specified in models.py. Leaving..."%opt.mode
  leave()
print " --> Running text2workspace for model: %s"%opt.mode
print " --> Input: Datacard%s.txt --> Output: Datacard%s_%s.root"%(opt.ext,opt.ext,opt.mode)

if not os.path.isdir("./t2w_jobs"): os.system("mkdir ./t2w_jobs")
# Open submission file to write to
fsub = open("./t2w_jobs/t2w_%s%s.sh"%(opt.mode,opt.ext),"w")
fsub.write("#!/bin/bash\n\n")
fsub.write("cd %s\n\n"%os.environ['PWD'])
fsub.write("eval `scramv1 runtime -sh`\n\n")
fsub.write("text2workspace.py Datacard%s.txt -o Datacard%s_%s.root %s %s"%(opt.ext,opt.ext,opt.mode,opt.common_opts,models[opt.mode]))
fsub.close()

# Change permission for file
os.system("chmod 775 ./t2w_jobs/t2w_%s%s.sh"%(opt.mode,opt.ext))

# Submit
subcmd = "qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G ./t2w_jobs/t2w_%s%s.sh"%(opt.mode,opt.ext)
if opt.dryRun: print "[DRY RUN] %s"%subcmd
else: run(subcmd)
