import os
import glob
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDir',dest='inputDir', default="", help='Input directory of jobs')
  return parser.parse_args()
(opt,args) = get_options()

subFiles = glob.glob("%s/*"%opt.inputDir)
for f in subFiles: 
  os.system("qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G %s"%f)
  #print "[DRY RUN] qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G %s"%f
