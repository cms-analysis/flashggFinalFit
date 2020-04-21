# Resubmit diagonal proc x cat signal fit
import os, re, sys
import glob
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--proc", dest='proc', default='', help="Category")
  parser.add_option("--cat", dest='cat', default='', help="Category")
  parser.add_option("--dryRun", dest='dryRun', default=False, action='store_true')
  return parser.parse_args()
(opt,args) = get_options()

if(opt.proc != '')&(opt.cat != ''): search = "proc:%s - cat:%s"%(opt.proc,opt.cat)
elif(opt.proc != ''): search = "proc:%s -"%opt.proc
elif(opt.cat != ''): search = "- cat:%s"%opt.cat
else: search = ''

if search == '': resubmitFiles = glob.glob("outdir_%s/sigfit/SignalFitJobs/*.sh"%opt.ext)
else:
  # Glob log files from initial signal fit
  logFiles = glob.glob("outdir_%s/sigfit/SignalFitJobs/*.log"%opt.ext)
  resubmitFiles = []
  # Loop over log files
  for lf in logFiles:
    with open(lf,"r") as fin:
      for line in fin:
	if(search in line): resubmitFiles.append(re.sub(".log","",lf))

# Resubmit files to batch
for f in resubmitFiles: 
  if opt.dryRun: print "[DRY-RUN] resubmit %s"%f
  else: os.system("qsub -q hep.q -l h_rt=0:20:0 %s"%f)
