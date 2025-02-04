import os, glob, sys
from optparse import OptionParser
from models import models

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG T2W RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")

def get_options():
  parser = OptionParser()
  parser.add_option("--outputDir", dest='outputDir', default='.', help="Output directory")
  parser.add_option("--outputName", dest='outputName', default='Datacard', help="Name of the datacard. Can be custom.")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Physics Model (specified in models.py)")
  parser.add_option('--ext',dest='ext', default="", help='In case running over datacard with extension')
  parser.add_option('--common_opts',dest='common_opts', default="-m 125 higgsMassRange=122,128", help='Common options')
  parser.add_option('--batch', dest='batch', default='condor', help="Batch system [SGE,IC,condor]")
  parser.add_option('--queue', dest='queue', default='workday', help="Condor queue")
  parser.add_option('--ncpus', dest='ncpus', default=4, type='int', help="Number of cpus")
  parser.add_option('--dryRun', dest='dryRun', action="store_true", default=False, help="Only create submission files")
  return parser.parse_args()
(opt,args) = get_options()

if opt.outputDir != '.':
  outputDir = opt.outputDir + "/Combine"
else:
  outputDir = opt.outputDir


def leave():
  print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG T2W RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  exit(1)

def run(cmd):
  print("%s\n\n"%cmd)
  os.system(cmd)

if opt.mode not in models: 
  print(" --> [ERROR] opt.mode (%s) is not specified in models.py. Leaving..."%opt.mode)
  leave()

print(" --> Running text2workspace for model: %s"%opt.mode)
if opt.ext != "":
  if opt.outputName == "Datacard":
    print(" --> Input: Datacard_%s.txt --> Output: Datacard_%s.root"%(opt.ext,opt.ext))
  else:
    print(" --> Input: %s.txt --> Output: %s.root"%(opt.outputName,opt.outputName))
else:
  if opt.outputName == "Datacard":
    print(" --> Input: Datacard%s.txt --> Output: Datacard%s_%s.root"%(opt.ext,opt.ext,opt.mode))
  else:
    print(" --> Input: %s.txt --> Output: %s.root"%(opt.outputName,opt.outputName))

if not os.path.isdir(f"{outputDir}/t2w_jobs"): os.system(f"mkdir {outputDir}/t2w_jobs")

if opt.ext != "":
  t2w_file_path = "%s/t2w_jobs/t2w_%s"%(outputDir,opt.ext)
else:
  t2w_file_path = "%s/t2w_jobs/t2w_%s"%(outputDir,opt.mode)
  
# Open submission file to write to
fsub = open(t2w_file_path+".sh","w")
fsub.write("#!/bin/bash\n\n")
fsub.write("cd %s\n\n"%os.environ['PWD'])
fsub.write("eval `scramv1 runtime -sh`\n\n")
if opt.ext != "":
  if opt.outputName == "Datacard":
    fsub.write("text2workspace.py %s/Datacard_%s.txt -o %s/Datacard_%s.root %s %s"%(outputDir,opt.ext,outputDir,opt.ext,opt.common_opts,models[opt.mode]))
  else:
    fsub.write("text2workspace.py %s/%s.txt -o %s/%s.root %s %s"%(outputDir,opt.outputName,outputDir,opt.outputName,opt.common_opts,models[opt.mode]))
else:
  if opt.outputName == "Datacard":
    fsub.write("text2workspace.py %s/Datacard%s.txt -o %s/Datacard%s_%s.root %s %s"%(outputDir,opt.ext,outputDir,opt.ext,opt.mode,opt.common_opts,models[opt.mode]))
  else:
    fsub.write("text2workspace.py %s/%s.txt -o %s/%s.root %s %s"%(outputDir,opt.outputName,outputDir,opt.outputName,opt.common_opts,models[opt.mode]))
fsub.close()

# Change permission for file
os.system("chmod 775 "+t2w_file_path+".sh")

# If using condor then also write submission file
if opt.batch == 'condor':
  f_cdr = open(t2w_file_path+".sh","w")
  if opt.ext != "":
    f_cdr_path = "%s/src/flashggFinalFit/Combine/t2w_jobs/t2w_%s"%(os.environ['CMSSW_BASE'],opt.ext)
  else:
    f_cdr_path = "%s/src/flashggFinalFit/Combine/t2w_jobs/t2w_%s"%(os.environ['CMSSW_BASE'],opt.mode)
  f_cdr.write("executable          = "+f_cdr_path+".sh\n")
  f_cdr.write("output              = "+f_cdr_path+".sh.out\n")
  f_cdr.write("error               = "+f_cdr_path+".sh.err\n")
  f_cdr.write("log                 = "+f_cdr_path+".sh.log\n")
  f_cdr.write('+AccountingGroup = "group_u_CMS.u_zh.users"\n')
  f_cdr.write("+JobFlavour         = \"%s\"\n"%opt.queue)
  f_cdr.write("RequestCpus         = %g\n"%opt.ncpus)
  f_cdr.write("queue\n")
  f_cdr.close()

# Submit
if outputDir != '.':
  if opt.batch == "condor": subcmd = "condor_submit -spool %s/t2w_jobs/t2w_%s%s.sub"%(outputDir,opt.mode,opt.ext)
  elif opt.batch == 'local': subcmd = "bash "+t2w_file_path+".sh"
  else: subcmd = "qsub -q hep.q -l h_rt=6:0:0 -l h_vmem=24G "+t2w_file_path+".sh"
  if opt.dryRun: print("[DRY RUN] %s"%subcmd)
  else: run(subcmd)

else:
  if opt.batch == "condor": 
    if os.path.realpath(os.environ['PWD']).startswith("/eos"):
      subcmd = "condor_submit -spool "+t2w_file_path+".sub"
    else:
      subcmd = "condor_submit "+t2w_file_path+".sub"
  elif opt.batch == 'local': subcmd = "bash "+t2w_file_path+".sh"
  else: subcmd = "qsub -q hep.q -l h_rt=6:0:0 -l h_vmem=24G "+t2w_file_path+".sh"
  if opt.dryRun: print("[DRY RUN] %s"%subcmd)
  else: run(subcmd)