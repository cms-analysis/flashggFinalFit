# Script to make migration + purity matrices and output yields table
#  * Read in PANDAS dataframe

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import numpy as np
import glob
import pickle
import math
import json
from collections import OrderedDict
# Scripts for plotting
from plottingTools import getEffSigma

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG CAT INFO RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG CAT INFO (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option("--inputEffSigma", dest="inputEffSigma", default=None, help="Load eff sigma from json")
  parser.add_option("--cats", dest="cats", default=None, help="Analysis categories. all = loop over cats and plot sum")
  parser.add_option("--parameterMap", dest="parameterMap", default=None, help="Comma separated pairs of model parameters:values,...")
  parser.add_option("--doBkgRenormalization", dest="doBkgRenormalization", default=False, action="store_true", help="Do Bkg renormalization")
  parser.add_option("--saveCatInfo", dest="saveCatInfo", default=False, action='store_true', help="Save category info to pkl file")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass,m_{#gamma#gamma},GeV", help="X-variable: name,title,units")
  parser.add_option("--pdfNBins", dest="pdfNBins", default=3200, type='int', help="Number of bins")
  return parser.parse_args()
(opt,args) = get_options()

# Open WS
if opt.inputWSFile is not None:
  print " --> Opening workspace: %s"%opt.inputWSFile
  f = ROOT.TFile(opt.inputWSFile)
  w = f.Get("w")
  # If required loadSnapshot
  if opt.loadSnapshot is not None: 
    print "    * Loading snapshot: %s"%opt.loadSnapshot
    w.loadSnapshot(opt.loadSnapshot)
  # Set parameters
  if opt.parameterMap is not None:
    print "    * Setting values of parameters: %s"%opt.parameterMap
    for kv in opt.parameterMap.split(","):
      k, v = kv.split(":")[0], kv.split(":")[1]
      w.var(k).setVal(float(v))

if opt.inputEffSigma is not None:
  with open(opt.inputEffSigma,"r") as jsonfile: effSigmaVals = json.load(jsonfile)

# Define xvariable and categories
xvar = w.var(opt.xvar.split(",")[0]) 
weight = ROOT.RooRealVar("weight","weight",0)
xvar.SetTitle(opt.xvar.split(",")[1])
xvar.setPlotLabel(opt.xvar.split(",")[1])
xvar.setUnit(opt.xvar.split(",")[2])
xvar_arglist, xvar_argset = ROOT.RooArgList(xvar), ROOT.RooArgSet(xvar)
chan = w.cat("CMS_channel")

# Extract the total SB/B models
sb_model, b_model = w.pdf("model_s"), w.pdf("model_b")

# Extract cats for opt.cats
if opt.cats == 'all':
  cats = []
  for cidx in range(chan.numTypes()):
    chan.setIndex(cidx)
    c = chan.getLabel()
    cats.append(c)
else: cats = opt.cats.split(",")

# Initiate dataframe to store cat info
_columns = ['cat','effSigma','sig','bkg','bkg_per_GeV','SoverSplusB']
catinfo_data = pd.DataFrame(columns=_columns)

for c in cats:
  sbpdf, bpdf = sb_model.getPdf(c), b_model.getPdf(c)
  h_sbpdf_tmp = sbpdf.createHistogram("h_sb_tmp_pdfNBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.pdfNBins))
  h_bpdf_tmp = bpdf.createHistogram("h_b_tmp_pdfNBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.pdfNBins))
  # Calculate yields
  SB, B = sbpdf.expectedEvents(xvar_argset), bpdf.expectedEvents(xvar_argset)
  S = SB-B 
  # If option doBkfRenormalization: renormalize B pdf to be S+B-S
  if opt.doBkgRenormalization:
    Bcorr = B-S
    SBcorr = B
    normFactor_B, normFactor_SB = Bcorr/B, SBcorr/SB
    h_sbpdf_tmp.Scale(normFactor_SB)
    h_bpdf_tmp.Scale(normFactor_B)
    B = Bcorr # set new bkg yield
  # Make signal pdf
  h_spdf_tmp = h_sbpdf_tmp-h_bpdf_tmp

  # Extract effSigma for signal model
  if opt.inputEffSigma is not None: effSigma = effSigmaVals[c]
  else: effSigma = getEffSigma(h_spdf_tmp) 
  # Calculate S/B yields in +-1sigma of peak
  rangeName = "effSigma_%s"%c
  xvar.setRange(rangeName,w.var("MH").getVal()-effSigma,w.var("MH").getVal()+effSigma)
  Beff = bpdf.createIntegral(xvar_argset,xvar_argset,rangeName).getVal()*B
  Beff_per_GeV = Beff/effSigma
  Seff = math.erf(1./math.sqrt(2))*S
  # Calc S/S+B
  SoverSplusB = Seff/(Seff+Beff)

  # Fill dataframe
  catinfo_data.loc[len(catinfo_data)] = [c,effSigma,Seff,Beff,Beff_per_GeV,SoverSplusB]

# Save dataframe
if opt.saveCatInfo:
  if not os.path.isdir("./pkl"): os.system("mkdir ./pkl")
  with open("./pkl/catInfo%s.pkl"%opt.ext,"w") as fD: pickle.dump(catinfo_data,fD)
  

