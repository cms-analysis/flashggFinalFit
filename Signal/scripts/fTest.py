# Python script to perform signal modelling fTest: extract number of gaussians for final fit
# * run per category over single mass point

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FTEST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
import ROOT
import pandas as pd
import pickle
import math
import os, sys
import json
from optparse import OptionParser
import glob
import re
from collections import OrderedDict as od

from commonTools import *
from commonObjects import *
from signalTools import *
from simultaneousFit import *
from plottingTools import *

MHLow, MHHigh = '120', '130'

def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FTEST (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  exit(0)

def get_options():
  parser = OptionParser()
  parser.add_option("--xvar", dest='xvar', default='CMS_hgg_mass', help="Observable to fit")
  parser.add_option("--inputWSDir", dest='inputWSDir', default='', help="Input flashgg WS directory")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--procs", dest='procs', default='', help="Signal processes")
  parser.add_option("--nProcsToFTest", dest='nProcsToFTest', default=5, type='int',help="Number of signal processes to fTest (ordered by sum entries), others are set to nRV=1,nWV=1. Set to -1 to run over all")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option('--mass', dest='mass', default='125', help="Mass point to fit")
  parser.add_option('--doPlots', dest='doPlots', default=False, action="store_true", help="Produce Signal fTest plots")
  parser.add_option('--nBins', dest='nBins', default=80, type='int', help="Number of bins for fit")
  parser.add_option('--threshold', dest='threshold', default=30, type='int', help="Threshold number of events")
  parser.add_option('--nGaussMax', dest='nGaussMax', default=5, type='int', help="Max number of gaussians to test")
  parser.add_option('--skipWV', dest='skipWV', default=False, action="store_true", help="Skip processing of WV case")
  # Minimizer options
  parser.add_option('--minimizerMethod', dest='minimizerMethod', default='TNC', help="(Scipy) Minimizer method")
  parser.add_option('--minimizerTolerance', dest='minimizerTolerance', default=1e-8, type='float', help="(Scipy) Minimizer toleranve")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
if opt.doPlots: 
  if not os.path.isdir("%s/outdir_%s/fTest/Plots"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/fTest/Plots"%(swd__,opt.ext))

# Load xvar to fit
nominalWSFileName = glob.glob("%s/output*"%(opt.inputWSDir))[0]
f0 = ROOT.TFile(nominalWSFileName,"read")
inputWS0 = f0.Get(inputWSName__)
xvar = inputWS0.var(opt.xvar)
xvarFit = xvar.Clone()
dZ = inputWS0.var("dZ")
aset = ROOT.RooArgSet(xvar,dZ)
f0.Close()

# Create MH var
MH = ROOT.RooRealVar("MH","m_{H}", int(MHLow), int(MHHigh))
MH.setUnit("GeV")
MH.setConstant(True)

# Loop over processes: extract sum entries and fill dict. Default nRV,nWV = 1,1
df = pd.DataFrame(columns=['proc','sumEntries','nRV','nWV'])
procYields = od()
for proc in opt.procs.split(","):
  WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,opt.mass,proc))[0]
  f = ROOT.TFile(WSFileName,"read")
  inputWS = f.Get(inputWSName__)
  d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(proc.split("_")[0]),opt.mass,sqrts__,opt.cat)),aset)
  df.loc[len(df)] = [proc,d.sumEntries(),1,1]
  inputWS.Delete()
  f.Close()

# Extract processes to perform fTest (i.e. first nProcsToFTest):
if( opt.nProcsToFTest == -1)|( opt.nProcsToFTest > len(opt.procs.split(",")) ): procsToFTest = opt.procs.split(",")
else: procsToFTest = list(df.sort_values('sumEntries',ascending=False)[0:opt.nProcsToFTest].proc.values)
for pidx, proc in enumerate(procsToFTest): 

  print("\n --> Process (%g): %s"%(pidx,proc))

  # Split dataset to RV/WV: ssf requires input as dict (with mass point as key)
  datasets_RV, datasets_WV = od(), od()
  WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,opt.mass,proc))[0]
  f = ROOT.TFile(WSFileName,"read")
  inputWS = f.Get(inputWSName__)
  d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(proc.split("_")[0]),opt.mass,sqrts__,opt.cat)),aset)
  datasets_RV[opt.mass] = splitRVWV(d,aset,mode="RV")
  datasets_WV[opt.mass] = splitRVWV(d,aset,mode="WV")

  # Run fTest: RV
  # If numEntries below threshold then keep as n = 1
  if datasets_RV[opt.mass].numEntries() < opt.threshold: continue  
  else:
    ssfs = od()
    min_reduced_chi2, nGauss_opt = 999, 1
    for nGauss in range(1,opt.nGaussMax+1):
      k = "nGauss_%g"%nGauss
      ssf = SimultaneousFit("fTest_RV_%g"%nGauss,proc,opt.cat,datasets_RV,xvar.Clone(),MH,MHLow,MHHigh,opt.mass,opt.nBins,0,opt.minimizerMethod,opt.minimizerTolerance,verbose=False)
      ssf.buildNGaussians(nGauss)
      ssf.runFit()
      ssf.buildSplines()
      if ssf.Ndof >= 1: 
        ssfs[k] = ssf
        if ssfs[k].getReducedChi2() < min_reduced_chi2: 
          min_reduced_chi2 = ssfs[k].getReducedChi2()
          nGauss_opt = nGauss
        print("   * (%s,%s,RV): nGauss = %g, chi^2/n(dof) = %.4f"%(proc,opt.cat,nGauss,ssfs[k].getReducedChi2()))
    # Set optimum
    df.loc[df['proc']==proc,'nRV'] = nGauss_opt
    # Make plots
    if( opt.doPlots )&( len(ssfs.keys())!=0 ):
      plotFTest(ssfs,_opt=nGauss_opt,_outdir="%s/outdir_%s/fTest/Plots"%(swd__,opt.ext),_extension="RV",_proc=proc,_cat=opt.cat,_mass=opt.mass)
      plotFTestResults(ssfs,_opt=nGauss_opt,_outdir="%s/outdir_%s/fTest/Plots"%(swd__,opt.ext),_extension="RV",_proc=proc,_cat=opt.cat,_mass=opt.mass)

  # Run fTest: WV
  # If numEntries below threshold then keep as n = 1
  if( datasets_WV[opt.mass].numEntries() < opt.threshold )|( opt.skipWV ): continue
  else:
    ssfs = od()
    min_reduced_chi2, nGauss_opt = 999, 1
    for nGauss in range(1,opt.nGaussMax+1):
      k = "nGauss_%g"%nGauss
      ssf = SimultaneousFit("fTest_WV_%g"%nGauss,proc,opt.cat,datasets_WV,xvar.Clone(),MH,MHLow,MHHigh,opt.mass,opt.nBins,0,opt.minimizerMethod,opt.minimizerTolerance,verbose=False)
      ssf.buildNGaussians(nGauss)
      ssf.runFit()
      ssf.buildSplines()
      if ssf.Ndof >= 1:
        ssfs[k] = ssf
        if ssfs[k].getReducedChi2() < min_reduced_chi2:
          min_reduced_chi2 = ssfs[k].getReducedChi2()
          nGauss_opt = nGauss
        print("   * (%s,%s,WV): nGauss = %g, chi^2/n(dof) = %.4f"%(proc,opt.cat,nGauss,ssfs[k].getReducedChi2()))
    # Set optimum
    df.loc[df['proc']==proc,'nWV'] = nGauss_opt
    # Make plots
    if( opt.doPlots )&( len(ssfs.keys())!=0 ):
      plotFTest(ssfs,_opt=nGauss_opt,_outdir="%s/outdir_%s/fTest/Plots"%(swd__,opt.ext),_extension="WV",_proc=proc,_cat=opt.cat,_mass=opt.mass)
      plotFTestResults(ssfs,_opt=nGauss_opt,_outdir="%s/outdir_%s/fTest/Plots"%(swd__,opt.ext),_extension="WV",_proc=proc,_cat=opt.cat,_mass=opt.mass)

  # Close ROOT file
  inputWS.Delete()
  f.Close()

# Make output
if not os.path.isdir("%s/outdir_%s/fTest/json"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/fTest/json"%(swd__,opt.ext))
ff = open("%s/outdir_%s/fTest/json/nGauss_%s.json"%(swd__,opt.ext,opt.cat),"w")
ff.write("{\n")
# Iterate over rows in dataframe: sorted by sumEntries
pitr = 1
for ir,r in df.sort_values('sumEntries',ascending=False).iterrows():
  k = "\"%s__%s\""%(r['proc'],opt.cat)
  ff.write("    %-90s : {\"nRV\":%s,\"nWV\":%s}"%(k,r['nRV'],r['nWV']))
  # Drop comma for last proc
  if pitr == len(df): ff.write("\n")
  else: ff.write(",\n")
  pitr += 1
ff.write("}")
ff.close()
