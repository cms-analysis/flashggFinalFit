import glob, os, re
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option("--ext", dest="ext", default="", help="Signal fit run extension")
  parser.add_option("--mode", dest="mode", default="fail", help="Type of jobs to resubmit [fail,run,not_done]")
  return parser.parse_args()
(opt,args) = get_options()

files = []
if opt.mode == "not_done": 
  all_files = glob.glob("./outdir_%s/sigfit/SignalFitJobs/*.sh"%(opt.ext))
  for f in all_files: 
    done_file = glob.glob("%s.done"%f)
    if len(done_file)==0: files.append(f)
  for f in files:
    #print " --> Resubmitting: %s"%f
    os.system("./%s"%f)
    #os.system("qsub -q hep.q -l h_rt=0:20:0 -l h_vmem=24G %s"%f)
else: 
  files = glob.glob("./outdir_%s/sigfit/SignalFitJobs/*.%s"%(opt.ext,opt.mode))
  for f in files:
    f_resubmit = re.sub(".%s"%opt.mode,"",f)
    print " --> Resubmitting: %s"%f_resubmit
    # Run script locally
    os.system("qsub -q hep.q -l h_rt=0:20:0 -l h_vmem=24G %s"%f_resubmit)
