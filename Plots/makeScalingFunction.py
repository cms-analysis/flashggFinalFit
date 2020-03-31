import os,sys,re
import ROOT
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWS", dest="inputWS", default = "", help="Input RooWorkspace")
  parser.add_option("--mode", dest="mode", default = "proc", help="Mode: [proc,cat]")
  parser.add_option("--poi", dest="poi", default = "r", help="Parameter of interest")
  parser.add_option("--poiRange", dest="poiRange", default = "-2,2", help="POI range")
  parser.add_option("--points", dest="points", default=200, help="Number of points in plot")
  parser.add_option("--obs", dest="obs", default = "ggH_0J_PTH_0_10", help="Observable")
  parser.add_option("--ext", dest="ext", default = "", help="Extension to save")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

# Extract normalisations
f = ROOT.TFile(opt.inputWS)
w = f.Get("w")
allNorms = w.allFunctions().selectByName("n_exp_final*%s*"%opt.obs)

# Extract nominal yield: if looking at process only need single normalisation
y0 = 0
nidx = 0
for norm in rooiter(allNorms):
  if(opt.mode == "proc")&(nidx > 0): continue 
  y0 += norm.getVal()
  nidx += 1

# Define poi range
x = np.linspace(float(opt.poiRange.split(",")[0]), float(opt.poiRange.split(",")[1]), int(opt.points))
w.var(opt.poi).setMin(float(opt.poiRange.split(",")[0]))
w.var(opt.poi).setMax(float(opt.poiRange.split(",")[1]))
y_norm = []
# Loop over norm and extract yields for differen tpoi values
for p in x:
  nidx = 0
  y = 0
  for norm in rooiter(allNorms):
    if(opt.mode == "proc")&(nidx > 0): continue
    w.var(opt.poi).setVal(p)
    y += norm.getVal()
    nidx += 1
  y_norm.append(y/y0)
y_norm = np.asarray(y_norm)

# Plot 
plt.figure(1)
plt.plot(x,y_norm)
plt.xlabel(opt.poi)
plt.ylabel(opt.obs)
plt.savefig("./ScalingFunctions/%s_vs_%s%s.png"%(opt.obs,opt.poi,opt.ext))
plt.savefig("./ScalingFunctions/%s_vs_%s%s.pdf"%(opt.obs,opt.poi,opt.ext))
#axes = plt.gca()
 
