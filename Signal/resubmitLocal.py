import glob, os, re
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option("--ext", dest="ext", default="", help="Signal fit run extension")
  parser.add_option("--mode", dest="mode", default="fail", help="Type of jobs to resubmit [fail,run]")
  return parser.parse_args()
(opt,args) = get_options()

files = glob.glob("./outdir_%s/sigfit/SignalFitJobs/*.%s"%(opt.ext,opt.mode))
for f in files:
  f_resubmit = re.sub(".%s"%opt.mode,"",f)
  print " --> Resubmitting: %s"%f_resubmit
  # Run script locally
  os.system("./%s"%f_resubmit)
  # If mode == fail and successfully ran job then delete .fail file (.run deletes automatically)
  if opt.mode == "fail": os.system("rm %s"%f)
