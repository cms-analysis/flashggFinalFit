# Script for submitting packager for signal models

import os, sys
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--cats', dest='cats', default='UntaggedTag_0,VBFTag_0', help="Define categories")
  parser.add_option('--ext', dest='ext', default='test', help="Extension: dropping year tag")
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Use if merging categories across years")
  parser.add_option('--years', dest='years', default='2016,2017,2018', help="Years")
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
  # Submit scripts to batch
  for cat_idx in range(len(opt.cats.split(","))):
    cat = opt.cats.split(",")[cat_idx]
    print " --> Category: %s (sub%g.sh)"%(cat,cat_idx)
    os.system("qsub -q hep.q -l h_rt=0:20:0 ./outdir_%s/packageJobs/sub%g.sh"%(opt.ext,cat_idx))

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
    # Submit scripts to batch
    for cat_idx in range(len(opt.cats.split(","))):
      cat = opt.cats.split(",")[cat_idx]
      print " --> Category: %s, Year: %s (sub%g.sh)"%(cat,year,cat_idx)
      os.system("qsub -q hep.q -l h_rt=0:20:0 ./outdir_%s_%s/packageJobs/sub%g.sh"%(opt.ext,year,cat_idx))
