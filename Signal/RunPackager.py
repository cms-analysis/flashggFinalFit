# Script for submitting packager for signal models

import os, sys
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--cats', dest='cats', default='UntaggedTag_0,VBFTag_0', help="Define categories")
  parser.add_option('--ext', dest='ext', default='test', help="Extension: dropping year tag")
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Use if merging categories across years")
  parser.add_option('--years', dest='years', default='2016,2017,2018', help="Years")
  parser.add_option('--skipMergingForCats', dest='skipMergingForCats', default='', help="Comma separated list of categories to skip year merging")
  parser.add_option('--dryRun', dest='dryRun', default=False, action="store_true", help="Dry run")
  parser.add_option('--batch', dest='batch', default='IC', help='Batch')
  return parser.parse_args()
(opt,args) = get_options()

if opt.mergeYears:
  if not os.path.isdir("outdir_%s"%opt.ext): os.system("mkdir ./outdir_%s"%opt.ext)
  if not os.path.isdir("outdir_%s/packageJobs"%opt.ext): os.system("mkdir ./outdir_%s/packageJobs"%opt.ext)
  # Write submission script
  for cat_idx in range(len(opt.cats.split(","))):
    cat = opt.cats.split(",")[cat_idx]
    f = open("./outdir_%s/packageJobs/sub%g.sh"%(opt.ext,cat_idx),'w')
    f.write("#!/bin/bash\n\n")
    f.write("cd %s/src/flashggFinalFit/Signal\n\n"%os.environ['CMSSW_BASE'])
    f.write("eval `scramv1 runtime -sh`\n\n")
    f.write("python python/packageSignal.py --cat %s --ext %s --mergeYears --years %s"%(cat,opt.ext,opt.years))
    f.close()
    if opt.batch == "condor":
      # Write condor submission file
      f = open("./outdir_%s/packageJobs/sub%g.sub"%(opt.ext,cat_idx),'w')
      f.write("executable          = %s/src/flashggFinalFit/Signal/outdir_%s/packageJobs/sub%g.sh\n"%(os.environ['CMSSW_BASE'],opt.ext,cat_idx))
      f.write("output              = %s/src/flashggFinalFit/Signal/outdir_%s/packageJobs/sub%g.sh.out\n"%(os.environ['CMSSW_BASE'],opt.ext,cat_idx))
      f.write("error               = %s/src/flashggFinalFit/Signal/outdir_%s/packageJobs/sub%g.sh.err\n"%(os.environ['CMSSW_BASE'],opt.ext,cat_idx))
      f.write("log                 = %s/src/flashggFinalFit/Signal/outdir_%s/packageJobs/sub%g.sh.log\n"%(os.environ['CMSSW_BASE'],opt.ext,cat_idx))
      f.write("+JobFlavour         = \"microcentury\"\n")
      f.write("queue\n")
      f.close()
  # Change permission of scripts
  os.system("chmod 775 ./outdir_%s/packageJobs/sub*.sh"%opt.ext)
  # Submit scripts to batch
  if not opt.dryRun:
    for cat_idx in range(len(opt.cats.split(","))):
      cat = opt.cats.split(",")[cat_idx]
      print " --> Category: %s (sub%g.sh)"%(cat,cat_idx)
      if opt.batch == "condor": os.system("condor_submit ./outdir_%s/packageJobs/sub%g.sub"%(opt.ext,cat_idx))
      else: os.system("qsub -q hep.q -l h_rt=0:20:0 ./outdir_%s/packageJobs/sub%g.sh"%(opt.ext,cat_idx))

else:
  for year in opt.years.split(","):
    if not os.path.isdir("outdir_%s_%s"%(opt.ext,year)):
      print " --> [ERROR] Outdir for this extension+year does not exist: ./outdir_%s_%s. Have you dropped the year tag? Leaving"%(opt.ext,year)
      sys.exit(1)
    if not os.path.isdir("outdir_%s_%s/packageJobs"%(opt.ext,year)): os.system("mkdir ./outdir_%s_%s/packageJobs"%(opt.ext,year))
    # Write submission script
    for cat_idx in range(len(opt.cats.split(","))):
      cat = opt.cats.split(",")[cat_idx]
      f = open("./outdir_%s_%s/packageJobs/sub%g.sh"%(opt.ext,year,cat_idx),'w')
      f.write("#!/bin/bash\n\n")
      f.write("cd %s/src/flashggFinalFit/Signal\n\n"%os.environ['CMSSW_BASE'])
      f.write("eval `scramv1 runtime -sh`\n\n")
      f.write("python python/packageSignal.py --cat %s --ext %s --years %s"%(cat,opt.ext,year))
      f.close()
    # Change permission of scripts
    os.system("chmod 775 ./outdir_%s_%s/packageJobs/sub*.sh"%(opt.ext,year))
    if not opt.dryRun:
      # Submit scripts to batch
      for cat_idx in range(len(opt.cats.split(","))):
        cat = opt.cats.split(",")[cat_idx]
        print " --> Category: %s, Year: %s (sub%g.sh)"%(cat,year,cat_idx)
        os.system("qsub -q hep.q -l h_rt=0:20:0 ./outdir_%s_%s/packageJobs/sub%g.sh"%(opt.ext,year,cat_idx))
