import os, glob

t2ws = glob.glob("t2w_*")
for t2w in t2ws: 
  mode = t2w.split("t2w_")[-1]
  os.system("qsub -q hep.q -l h_rt=2:0:0 -l h_vmem=24G %s"%t2w)
