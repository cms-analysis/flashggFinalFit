# Script to make migration + purity matrices and output yields table
#  * Read in PANDAS dataframe

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import math
import json
from collections import OrderedDict
# Scripts for plotting
from plottingTools import getEffSigma, makeSplusBPlot

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG MODEL PLOTTER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG MODEL PLOTTER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

#ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--cat", dest="cat", default=None, help="Analysis category. all = loop over cats and plot sum")
  parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="Unblind signal region")
  parser.add_option("--blindingRegion", dest="blindingRegion", default="116,134", help="Region in xvar to blind")
  parser.add_option("--dataScaler", dest="dataScaler", default=1., type='float', help="Scaling term for data histogram")
  parser.add_option("--doBkgRenormalization", dest="doBkgRenormalization", default=False, action="store_true", help="Do Bkg renormalization")
  parser.add_option("--doBands", dest="doBands", default=False, action="store_true", help="Do +-1/2sigma bands for bkg model")
  parser.add_option("--doZeroes", dest="doZeroes", default=False, action="store_true", help="Add error of unity to zero bins to show on plot")
  parser.add_option("--skipIndividualCatPlots", dest="skipIndividualCatPlots", default=False, action="store_true", help="Skip plotting of individual categories")
  parser.add_option("--doWeightedPlot", dest="doWeightedPlot", default=False, action="store_true", help="Do S/S+B weighted plot if cat=all")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option("--parameterMap", dest="parameterMap", default=None, help="Comma separated pairs of model parameters:values,...")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--mass", dest="mass", default=None, help="Higgs mass")
  parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass,m_{#gamma#gamma},GeV", help="X-variable: name,title,units")
  parser.add_option("--nBins", dest="nBins", default=80, type='int', help="Number of bins")
  parser.add_option("--pdfNBins", dest="pdfNBins", default=3200, type='int', help="Number of bins")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--translatePOIs", dest="translatePOIs", default=None, help="JSON to store poi translations")
  parser.add_option("--problematicCats", dest="problematicCats", default='', help='Problematic analysis categories to skip when processing all')
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
  # Also loop over parameters in map and set
  if opt.parameterMap is not None:
    if opt.loadSnapshot is not None:
      print " --> [WARNING] Already loaded snapshot. Also setting parameters from opt.parameterMap"
    for kv in opt.parameterMap.split(","):
      k, v = kv.split(":")[0], kv.split(":")[1]
      w.var(k).setVal(float(v))

# Define blinding region
blindingRegion = [float(opt.blindingRegion.split(",")[0]),float(opt.blindingRegion.split(",")[1])]
# Define xvariable and categories
if opt.mass is not None: w.var("MH").setVal(float(opt.mass))
xvar = w.var(opt.xvar.split(",")[0]) 
xvar.SetTitle(opt.xvar.split(",")[1])
xvar.setPlotLabel(opt.xvar.split(",")[1])
xvar.setUnit(opt.xvar.split(",")[2])
xvar_arglist, xvar_argset = ROOT.RooArgList(xvar), ROOT.RooArgSet(xvar)
chan = w.cat("CMS_channel")
# Extract the total SB/B models
sb_model, b_model = w.pdf("model_s"), w.pdf("model_b")

# Extract dataset for opt.cat
d_obs = w.data("data_obs")
data_cats = OrderedDict()
print " --> Extracting datasets"
for cidx in range(chan.numTypes()):
  chan.setIndex(cidx)
  if(opt.cat!='all')&(chan.getLabel()!=opt.cat): continue
  data_cats[chan.getLabel()] = ROOT.RooDataSet("d_%s"%chan.getLabel(),"d_%s"%chan.getLabel(),xvar_argset)
# Loop over bins and add entry for each "weight" to cat datasets 
for i in range(d_obs.numEntries()):
  p = d_obs.get(i)
  if(opt.cat!='all')&(p.getCatLabel("CMS_channel")!=opt.cat): continue
  nent = int(d_obs.weight())
  for ient in range(nent): data_cats[p.getCatLabel("CMS_channel")].add(p)

# Loop over categories
cats = data_cats.keys()
catsWeights = {}
# If option doWeightedPlot: first extract S/S+B weights for each category
if "RECO" in opt.cat:
#if(opt.cat =='all')&(opt.doWeightedPlot):
  print " --> Extracting S/S+B weights for categories"
  Stot, Swtot = 0, 0
  for cidx in range(len(cats)):
    c = cats[cidx]
    d = data_cats[c]
    if c in opt.problematicCats.split(","): continue
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
    effSigma = getEffSigma(h_spdf_tmp) 
    # Calculate S/B yields in +-1sigma of peak
    rangeName = "effSigma_%s"%c
    xvar.setRange(rangeName,w.var("MH").getVal()-effSigma,w.var("MH").getVal()+effSigma)
    Beff = bpdf.createIntegral(xvar_argset,xvar_argset,rangeName).getVal()*B
    Seff = math.erf(1./math.sqrt(2))*S
    # Caclualte weight for cat
    wcat = Seff/(Seff+Beff)
    catsWeights[c] = wcat
    Stot += S
    Swtot += S*wcat
  for c in cats: catsWeights[c] *= (Stot/Swtot)

for cidx in range(len(cats)):
  c = cats[cidx]
  d = data_cats[c]
  if c in opt.problematicCats.split(","): continue
  print " --> Processing category: %s"%c

  # Create data histogram
  print "    * creating data histogram"
  h_data = xvar.createHistogram("h_data_%s"%c, ROOT.RooFit.Binning(opt.nBins))
  h_data.SetBinErrorOption(ROOT.TH1.kPoisson)
  if opt.unblind: d.fillHistogram(h_data,xvar_arglist)
  else: d.reduce("%s<%f|%s>%f"%(xvar.GetName(),blindingRegion[0],xvar.GetName(),blindingRegion[1])).fillHistogram(h_data,xvar_arglist)

  # Scale data histogram
  h_data.Scale(opt.dataScaler)

  # If option doZeroes: add error of +-unity for zero bins
  if opt.doZeroes:
    for ibin in range(1,h_data.GetNbinsX()+1):
      bcenter = h_data.GetBinCenter(ibin)
      # Skip blinded region
      if( not opt.unblind )&(bcenter > blindingRegion[0])&(bcenter < blindingRegion[1]): continue 
      if h_data.GetBinContent(ibin)==0.: h_data.SetBinError(ibin,1)

  # Extract pdfs for category and create histograms
  print "    * creating pdf histograms: S+B, B"
  sbpdf, bpdf = sb_model.getPdf(c), b_model.getPdf(c)
  h_sbpdf = {'pdfNBins':sbpdf.createHistogram("h_sb_pdfNBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.pdfNBins)),
             'nBins':sbpdf.createHistogram("h_sb_nBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.nBins))
            }
  h_bpdf = {'pdfNBins':bpdf.createHistogram("h_b_pdfNBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.pdfNBins)),
             'nBins':bpdf.createHistogram("h_b_nBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.nBins))
            }
  # Calculate yields
  SB, B = sbpdf.expectedEvents(xvar_argset), bpdf.expectedEvents(xvar_argset)
  S = SB-B
  # If option doBkfRenormalization: renormalize B pdf to be S+B-S
  if opt.doBkgRenormalization:
    print "    * fixing B normalization"
    Bcorr = B-S
    SBcorr = B
    normFactor_B, normFactor_SB = Bcorr/B, SBcorr/SB
    for h in h_sbpdf.itervalues(): h.Scale(normFactor_SB)
    for h in h_bpdf.itervalues(): h.Scale(normFactor_B)
    print "    * Yield for category: S = %.2f, B=%.2f"%(S,Bcorr)
  else: print "    * Yield for category: S = %.2f, B=%.2f"%(S,B)

  # Extract signal pdf
  print "    * creating pdf histogram: S"
  h_spdf = {'pdfNBins':h_sbpdf['pdfNBins']-h_bpdf['pdfNBins'],
            'nBins':h_sbpdf['nBins']-h_bpdf['nBins']
           }
  
  # Scale pdf histograms to match binning used
  xvar_range = int(xvar.getBinning().highBound()-xvar.getBinning().lowBound())
  if opt.nBins != xvar_range:
    print "    * scaling pdf histograms to match binning of data"
    for h_ipdf in [h_sbpdf,h_bpdf,h_spdf]:
      for h in h_ipdf.itervalues(): h.Scale(float(xvar_range)/opt.nBins)

  # Create ratio histograms
  print "    * creating ratio histograms"
  h_bpdf_ratio = h_bpdf['pdfNBins']-h_bpdf['pdfNBins']
  h_spdf_ratio = h_spdf['pdfNBins'].Clone()
  h_data_ratio = h_data.Clone()
  h_data_ratio.Reset()
  for ibin in range(1,h_data.GetNbinsX()+1):
    bcenter = h_data.GetBinCenter(ibin)
    if(not opt.unblind)&(bcenter>blindingRegion[0])&(bcenter<blindingRegion[1]): continue
    bval, berr = h_data.GetBinContent(ibin), h_data.GetBinError(ibin)
    bkgval = h_bpdf['nBins'].GetBinContent(ibin)
    h_data_ratio.SetBinContent(ibin,bval-bkgval)
    h_data_ratio.SetBinError(ibin,berr)

  # Sum histograms if processing all categories
  if opt.cat == 'all':
    print "    * adding histogram to sum"
    if cidx == 0:
      h_data_all = h_data.Clone()
      h_data_ratio_all = h_data_ratio.Clone()
      h_sbpdf_all = {'pdfNBins':h_sbpdf['pdfNBins'].Clone(),'nBins':h_sbpdf['nBins'].Clone()}
      h_bpdf_all = {'pdfNBins':h_bpdf['pdfNBins'].Clone(),'nBins':h_bpdf['nBins'].Clone()}
      h_bpdf_ratio_all = h_bpdf_ratio.Clone()
      h_spdf_all = {'pdfNBins':h_spdf['pdfNBins'].Clone(),'nBins':h_spdf['nBins'].Clone()}
      h_spdf_ratio_all = h_spdf_ratio.Clone()
    else:
      h_data_all += h_data.Clone()
      h_data_ratio_all += h_data_ratio.Clone()
      for b,h in h_sbpdf.iteritems(): h_sbpdf_all[b] += h.Clone()
      for b,h in h_bpdf.iteritems(): h_bpdf_all[b] += h.Clone()
      h_bpdf_ratio_all += h_bpdf_ratio.Clone()
      for b,h in h_spdf.iteritems(): h_spdf_all[b] += h.Clone()
      h_spdf_ratio_all += h_spdf_ratio.Clone()

  # Make plot for individual cats
  if not opt.skipIndividualCatPlots:
    print "    * making plot"
    if not os.path.isdir("./SplusBModels%s"%(opt.ext)): os.system("mkdir ./SplusBModels%s"%(opt.ext))
    makeSplusBPlot(w,h_data,h_sbpdf,h_bpdf,h_spdf,h_data_ratio,h_bpdf_ratio,h_spdf_ratio,c,opt)

  # Delete histograms
  h_data.Delete()
  h_data_ratio.Delete()
  for h in h_sbpdf.itervalues(): h.Delete()
  for h in h_bpdf.itervalues(): h.Delete()
  h_bpdf_ratio.Delete()
  for h in h_spdf.itervalues(): h.Delete()
  h_spdf_ratio.Delete()
  print "    * finished processing\n"

# Finished processing individual categories: if all then plot all
if opt.cat == 'all':
  if not os.path.isdir("./SplusBModels%s"%(opt.ext)): os.system("mkdir ./SplusBModels%s"%(opt.ext))
  print " --> Making plot for all categories"
  makeSplusBPlot(w,h_data_all,h_sbpdf_all,h_bpdf_all,h_spdf_all,h_data_ratio_all,h_bpdf_ratio_all,h_spdf_ratio_all,'all',opt)
