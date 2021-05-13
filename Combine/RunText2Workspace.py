import os, glob, sys
from optparse import OptionParser
from models import models

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG T2W RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "

def get_options():
  parser = OptionParser()
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Physics Model (specified in models.py)")
  parser.add_option('--ext',dest='ext', default="", help='In case running over datacard with extension')
  parser.add_option('--common_opts',dest='common_opts', default="-m 125 higgsMassRange=122,128", help='Common options')
  parser.add_option('--batch', dest='batch', default='SGE', help="Batch system [SGE,IC,condor]")
  parser.add_option('--queue', dest='queue', default='workday', help="Condor queue")
  parser.add_option('--ncpus', dest='ncpus', default=4, type='int', help="Number of cpus")
  parser.add_option('--dryRun', dest='dryRun', action="store_true", default=False, help="Only create submission files")
  return parser.parse_args()
(opt,args) = get_options()

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG T2W RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  exit(1)

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

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

# If using condor then also write submission file
if opt.batch == 'condor':
  f_cdr = open("./t2w_jobs/t2w_%s%s.sub"%(opt.mode,opt.ext),"w")
  f_cdr.write("executable          = %s/src/flashggFinalFit/Combine/t2w_jobs/t2w_%s%s.sh\n"%(os.environ['CMSSW_BASE'],opt.mode,opt.ext))
  f_cdr.write("output              = %s/src/flashggFinalFit/Combine/t2w_jobs/t2w_%s%s.sh.out\n"%(os.environ['CMSSW_BASE'],opt.mode,opt.ext))
  f_cdr.write("error               = %s/src/flashggFinalFit/Combine/t2w_jobs/t2w_%s%s.sh.err\n"%(os.environ['CMSSW_BASE'],opt.mode,opt.ext))
  f_cdr.write("log                 = %s/src/flashggFinalFit/Combine/t2w_jobs/t2w_%s%s.sh.log\n"%(os.environ['CMSSW_BASE'],opt.mode,opt.ext))
  f_cdr.write("+JobFlavour         = \"%s\"\n"%opt.queue)
  f_cdr.write("RequestCpus         = %g\n"%opt.ncpus)
  f_cdr.write("queue\n")
  f_cdr.close()

# Submit
if opt.batch == "condor": subcmd = "condor_submit ./t2w_jobs/t2w_%s%s.sub"%(opt.mode,opt.ext)
elif opt.batch == 'local': subcmd = "bash ./t2w_jobs/t2w_%s%s.sh"%(opt.mode,opt.ext)
else: subcmd = "qsub -q hep.q -l h_rt=6:0:0 -l h_vmem=24G ./t2w_jobs/t2w_%s%s.sh"%(opt.mode,opt.ext)
if opt.dryRun: print "[DRY RUN] %s"%subcmd
else: run(subcmd)
