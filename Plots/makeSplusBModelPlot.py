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
from plottingTools import getEffSigma, makeSplusBPlot

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG MODEL PLOTTER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG MODEL PLOTTER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option("--cats", dest="cats", default=None, help="Analysis categories. all = loop over cats and plot sum")
  parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="Unblind signal region")
  parser.add_option("--blindingRegion", dest="blindingRegion", default="116,134", help="Region in xvar to blind")
  parser.add_option("--dataScaler", dest="dataScaler", default=1., type='float', help="Scaling term for data histogram")
  parser.add_option("--doBkgRenormalization", dest="doBkgRenormalization", default=False, action="store_true", help="Do Bkg renormalization")
  parser.add_option("--doBands", dest="doBands", default=False, action="store_true", help="Do +-1/2sigma bands for bkg model")
  parser.add_option("--doToyVeto", dest="doToyVeto", default=False, action="store_true", help="Veto non-sensical toys with 0 as first entry in bin")
  parser.add_option("--loadToyYields", dest="loadToyYields", default='', help="Load pkl file storing toy yields in dataframe")
  parser.add_option("--saveToyYields", dest="saveToyYields", default=False, action="store_true", help="Save toy yields dataframe")
  parser.add_option("--doZeroes", dest="doZeroes", default=False, action="store_true", help="Add error of unity to zero bins to show on plot")
  parser.add_option("--skipIndividualCatPlots", dest="skipIndividualCatPlots", default=False, action="store_true", help="Skip plotting of individual categories")
  parser.add_option("--doSumCategories", dest="doSumCategories", default=False, action="store_true", help="Do plot summing the categories being processed")
  parser.add_option("--doCatWeights", dest="doCatWeights", default=False, action="store_true", help="Do S/S+B weighted plot")
  parser.add_option("--loadWeights", dest="loadWeights", default='', help="JSON file storing category weights")
  parser.add_option("--saveWeights", dest="saveWeights", default=False, action='store_true', help="Save category weights to json file")
  parser.add_option("--parameterMap", dest="parameterMap", default=None, help="Comma separated pairs of model parameters:values,...")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--mass", dest="mass", default=None, help="Higgs mass")
  parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass,m_{#gamma#gamma},GeV", help="X-variable: name,title,units")
  parser.add_option("--nBins", dest="nBins", default=80, type='int', help="Number of bins")
  parser.add_option("--pdfNBins", dest="pdfNBins", default=3200, type='int', help="Number of bins")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--translatePOIs", dest="translatePOIs", default=None, help="JSON to store poi translations")
  parser.add_option("--problematicCats", dest="problematicCats", default='', help='Problematic analysis categories to skip when processing all')
  parser.add_option("--doHHMjjFix", dest="doHHMjjFix", default=False, action="store_true", help="Do fix for HH analysis where some cats have different Mjj var")
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
weight = ROOT.RooRealVar("weight","weight",0)
xvar.SetTitle(opt.xvar.split(",")[1])
xvar.setPlotLabel(opt.xvar.split(",")[1])
xvar.setUnit(opt.xvar.split(",")[2])
xvar_arglist, xvar_argset = ROOT.RooArgList(xvar), ROOT.RooArgSet(xvar)
wxvar_arglist, wxvar_argset = ROOT.RooArgList(xvar,weight), ROOT.RooArgSet(xvar,weight)
chan = w.cat("CMS_channel")

# Define HH fix variable
catsfix = ['DoubleHTag_10_13TeV','DoubleHTag_11_13TeV']
if opt.doHHMjjFix:
  xvarfix = w.var("%s_90GeV"%opt.xvar.split(",")[0])
  xvarfix.SetTitle(opt.xvar.split(",")[1])
  xvarfix.setPlotLabel(opt.xvar.split(",")[1])
  xvarfix.setUnit(opt.xvar.split(",")[2])
  xvarfix_arglist, xvarfix_argset = ROOT.RooArgList(xvarfix), ROOT.RooArgSet(xvarfix)
  wxvarfix_arglist, wxvarfix_argset = ROOT.RooArgList(xvarfix,weight), ROOT.RooArgSet(xvarfix,weight)
  fixrangeRatio = (xvarfix.getMax()-xvarfix.getMin())/(xvar.getMax()-xvar.getMin())
  print " --> HH fix: using Mjj_90GeV variable for cats: %s"%(",".join(catsfix))
  # Check: number of bins for 
  if not (fixrangeRatio*opt.nBins)%1 == 0:
    print "     * [ERROR] nBins for Mjj_90GeV is not an integer. Please use appropriate opt.nBins" 
    leave()  
  if not (fixrangeRatio*opt.pdfNBins)%1 == 0:
    print "     * [ERROR] pdfNBins for Mjj_90GeV is not an integer. Please use appropriate opt.pdfNBins" 
    leave()

# Extract the total SB/B models
sb_model, b_model = w.pdf("model_s"), w.pdf("model_b")

# Extract dataset for opt.cats
d_obs = w.data("data_obs")
data_cats = OrderedDict()
wdata_cats = OrderedDict()
for cidx in range(chan.numTypes()):
  chan.setIndex(cidx)
  c = chan.getLabel()
  if(opt.cats!='all')&(c not in opt.cats.split(",")): continue
  if( opt.doHHMjjFix )&( c in catsfix ): _xvar_argset, _wxvar_argset = xvarfix_argset, wxvarfix_argset
  else: _xvar_argset, _wxvar_argset = xvar_argset, wxvar_argset
  data_cats[c] = ROOT.RooDataSet("d_%s"%c,"d_%s"%c,_xvar_argset)
  wdata_cats[c] = ROOT.RooDataSet("wd_%s"%c,"wd_%s"%c,_wxvar_argset,"weight")

# Define cateogries
cats = data_cats.keys()

# Load cat weights from json file if specified
if opt.loadWeights != '':
  print " --> Loading category S/S+B weights from json file: %s"%opt.loadWeights
  with open(opt.loadWeights) as jsonfile: catsWeights = json.load(jsonfile)
  # Check all cats are in loaded weights file
  for c in cats:
    if c not in catsWeights: 
      print " --> [ERROR] category %s is not in S/S+B weights json. Leaving..."
      leave()
else:
  # Loop over categories to extract weights
  catsWeights = {}
  # If option doCatWeights: first extract S/S+B weights for each category
  if opt.doCatWeights:
    print " --> Extracting S/S+B weights for categories"
    Stot, Swtot = 0, 0
    for cidx in range(len(cats)):
      c = cats[cidx]
      if c in opt.problematicCats.split(","): continue
      if( opt.doHHMjjFix )&( c in catsfix ): _xvar, _xvar_argset = xvarfix, xvarfix_argset
      else: _xvar, _xvar_argset = xvar, xvar_argset
      sbpdf, bpdf = sb_model.getPdf(c), b_model.getPdf(c)
      h_sbpdf_tmp = sbpdf.createHistogram("h_sb_tmp_pdfNBins_%s"%c,_xvar,ROOT.RooFit.Binning(opt.pdfNBins))
      h_bpdf_tmp = bpdf.createHistogram("h_b_tmp_pdfNBins_%s"%c,_xvar,ROOT.RooFit.Binning(opt.pdfNBins))
      # Calculate yields
      SB, B = sbpdf.expectedEvents(_xvar_argset), bpdf.expectedEvents(_xvar_argset)
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
      Beff = bpdf.createIntegral(_xvar_argset,_xvar_argset,rangeName).getVal()*B
      Seff = math.erf(1./math.sqrt(2))*S
      # Caclualte weight for cat
      wcat = Seff/(Seff+Beff)
      catsWeights[c] = wcat
      print "   * %s: S = %.2f, B = %.2f --> effSigma = %.2f, S_eff = %.2f, B_eff = %.2f"%(c,S,B,effSigma,Seff,Beff)
      Stot += S
      Swtot += S*wcat
    # Renormalise to nominal signal yield
    for c in cats: catsWeights[c] *= (Stot/Swtot)
    # Save cat weights if specified
    if opt.saveWeights:
      print "      * Saving S/S+B weights to json file: ./jsons/catsWeights_sospb%s_%s.json"%(opt.ext,opt.xvar.split(",")[0])
      if not os.path.isdir("./jsons"): os.system("mkdir ./jsons")
      with open("./jsons/catsWeights_sospb%s_%s.json"%(opt.ext,opt.xvar.split(",")[0]),'w') as jsonfile: json.dump(catsWeights,jsonfile)

# Fill datasets
print " --> Extracting datasets"
# Loop over bins and add entry for each "weight" to cat datasets 
for i in range(d_obs.numEntries()):
  p = d_obs.get(i)
  if(opt.cats!='all')&(p.getCatLabel("CMS_channel") not in opt.cats.split(",")): continue
  nent = int(d_obs.weight())
  for ient in range(nent): data_cats[p.getCatLabel("CMS_channel")].add(p)
  if opt.doCatWeights: 
    for ient in range(nent): wdata_cats[p.getCatLabel("CMS_channel")].add(p,catsWeights[p.getCatLabel("CMS_channel")])

# if opt.doBands: make dataframe storing toy yields in each bin
if opt.doBands:
  if opt.loadToyYields != '':
    print " --> Loading toy yields for +-1/2sigma bands from %s"%opt.loadToyYields
    with open(opt.loadToyYields,"rb") as fD: df_bands = pickle.load(fD)
  else:
    print " --> Extracting toy yields for +-1/2sigma bands"
    # Define columns
    _columns = []
    for cat in cats:
      for ibin in range(1,opt.nBins+1):	_columns.append("%s_%g"%(cat,ibin))
    if opt.doSumCategories: 
      for ibin in range(1,opt.nBins+1):_columns.append("sum_%g"%ibin)
      if opt.doCatWeights: 
	for ibin in range(1,opt.nBins+1):_columns.append("wsum_%g"%ibin)
    # Create dataframe
    df_bands = pd.DataFrame(columns=_columns)
    # Loop over toys file and add row for each toy dataset
    toyFiles = glob.glob("./SplusBModels%s/toys/toy_*.root"%opt.ext)
    if len(toyFiles) == 0:
      print "     * [ERROR] No toys files of form ./SplusBModels%s/toys/toy_*.root. Skipping bands"%opt.ext
      opt.doBands = False
    else:
      for tidx in range(len(toyFiles)):
        print " --> Processing toy (%g/%g) ::: %s"%(tidx,len(toyFiles),toyFiles[tidx])
	ftoy = ROOT.TFile(toyFiles[tidx])
	toy = ftoy.Get("toys/toy_asimov")
        # Fla for vetoing toy
        vetoToy = False
	# Save bin contents in dict
	values = {}
	# Add columns for summing categories
        for cat in cats:
          for ibin in range(1,opt.nBins+1): values['%s_%g'%(cat,ibin)] = 0
	if opt.doSumCategories:
	  for ibin in range(1,opt.nBins+1): values['sum_%g'%ibin] = 0
	  if opt.doCatWeights:
	    for ibin in range(1,opt.nBins+1): values['wsum_%g'%ibin] = 0
	# Loop over cats
	for cidx in range(chan.numTypes()):
	  chan.setIndex(cidx)
	  c = chan.getLabel()
	  if( opt.cats == 'all' )|( c in opt.cats.split(",") ):
            if( opt.doHHMjjFix )&( c in catsfix ): 
              _xvar, _xvar_arglist = xvarfix, xvarfix_arglist
            else:
              _xvar, _xvar_arglist = xvar, xvar_arglist
	    dtoy = toy.reduce("CMS_channel==CMS_channel::%g"%(cidx))
	    htoy = _xvar.createHistogram("h_%s"%c,ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
	    dtoy.fillHistogram(htoy,_xvar_arglist)
	    for ibin in range(1,htoy.GetNbinsX()+1): 
	      v = htoy.GetBinContent(ibin)
              if v!=v: vetoToy = True # Veto toys which have a NaN
	      values['%s_%g'%(c,ibin)] = v
	      if opt.doSumCategories:
	        values['sum_%g'%ibin] += v
	        if opt.doCatWeights: values['wsum_%g'%ibin] += v*catsWeights[c]
            # Option for vetoing toy
            if opt.doToyVeto:
              if values['%s_1'%c] == 0: vetoToy = True
	    # Clear memory
	    htoy.Delete()
	    dtoy.Delete()
        toy.Delete()
        ftoy.Close()
	# Add values to dataframe
	if not vetoToy: df_bands.loc[len(df_bands)] = values
        else: print "   --> Toy veto: zero entries in first bin"
      # Savin toy yields dataframe to pickle file
      if opt.saveToyYields:
        print "      * Saving toy yields to: SplusBModels%s/toyYields_%s.pkl"%(opt.ext,opt.xvar.split(",")[0])
        with open("SplusBModels%s/toyYields_%s.pkl"%(opt.ext,opt.xvar.split(",")[0]),"w") as fD: pickle.dump(df_bands,fD)

# Process each category separately
for cidx in range(len(cats)):
  c = cats[cidx]
  d = data_cats[c]
  wd = wdata_cats[c]
  if c in opt.problematicCats.split(","): continue
  # If HH fix then set up which vars to use
  if( opt.doHHMjjFix )&( c in catsfix ):
    _xvar, _xvar_argset, _xvar_arglist = xvarfix, xvarfix_argset, xvarfix_arglist 
    _reduceRange = [xvarfix.getMin(),xvarfix.getMax()]
  else:
    _xvar, _xvar_argset, _xvar_arglist = xvar, xvar_argset, xvar_arglist
    _reduceRange = None

  print " --> Processing category: %s"%c

  # Create data histogram (+weighted)
  print "    * creating data histogram"
  h_data = _xvar.createHistogram("h_data_%s"%c, ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
  h_data.SetBinErrorOption(ROOT.TH1.kPoisson)
  if opt.unblind: d.fillHistogram(h_data,_xvar_arglist)
  else: d.reduce("%s<%f|%s>%f"%(_xvar.GetName(),blindingRegion[0],_xvar.GetName(),blindingRegion[1])).fillHistogram(h_data,_xvar_arglist)
  if opt.doCatWeights:
    h_wdata = _xvar.createHistogram("h_wdata_%s"%c, ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
    h_wdata.SetBinErrorOption(ROOT.TH1.kPoisson)
    if opt.unblind: wd.fillHistogram(h_wdata,_xvar_arglist)
    else: wd.reduce("%s<%f|%s>%f"%(_xvar.GetName(),blindingRegion[0],_xvar.GetName(),blindingRegion[1])).fillHistogram(h_wdata,_xvar_arglist)

  # Scale data histogram
  h_data.Scale(opt.dataScaler)
  if opt.doCatWeights: h_wdata.Scale(opt.dataScaler)

  # If option doZeroes: add error of +-unity for zero bins
  if opt.doZeroes:
    for ibin in range(1,h_data.GetNbinsX()+1):
      bcenter = h_data.GetBinCenter(ibin)
      # Skip blinded region
      if( not opt.unblind )&(bcenter > blindingRegion[0])&(bcenter < blindingRegion[1]): continue 
      if h_data.GetBinContent(ibin)==0.: 
        h_data.SetBinError(ibin,1)
        if opt.doCatWeights: h_wdata.SetBinError(ibin,catsWeights[c])

  # Extract pdfs for category and create histograms
  print "    * creating pdf histograms: S+B, B"
  sbpdf, bpdf = sb_model.getPdf(c), b_model.getPdf(c)
  h_sbpdf = {'pdfNBins':sbpdf.createHistogram("h_sb_pdfNBins_%s"%c,_xvar,ROOT.RooFit.Binning(opt.pdfNBins,xvar.getMin(),xvar.getMax())),
             'nBins':sbpdf.createHistogram("h_sb_nBins_%s"%c,_xvar,ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
            }
  h_bpdf = {'pdfNBins':bpdf.createHistogram("h_b_pdfNBins_%s"%c,_xvar,ROOT.RooFit.Binning(opt.pdfNBins,xvar.getMin(),xvar.getMax())),
             'nBins':bpdf.createHistogram("h_b_nBins_%s"%c,_xvar,ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
            }
  # Calculate yields
  SB, B = sbpdf.expectedEvents(_xvar_argset), bpdf.expectedEvents(_xvar_argset)
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

  # Create weighted pdf histograms
  if opt.doCatWeights:
    print "     * creating S/S+B weighted pdf histograms"
    h_wsbpdf = {'pdfNBins':h_sbpdf['pdfNBins'].Clone(),'nBins':h_sbpdf['nBins'].Clone()}
    h_wbpdf = {'pdfNBins':h_bpdf['pdfNBins'].Clone(),'nBins':h_bpdf['nBins'].Clone()}
    h_wspdf = {'pdfNBins':h_spdf['pdfNBins'].Clone(),'nBins':h_spdf['nBins'].Clone()}
    for h_ipdf in [h_wsbpdf,h_wbpdf,h_wspdf]:
      for h in h_ipdf.itervalues(): h.Scale(catsWeights[c])
  
  # Create ratio histograms (+weighted)
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
  if opt.doCatWeights:
    h_wbpdf_ratio = h_wbpdf['pdfNBins']-h_wbpdf['pdfNBins']
    h_wspdf_ratio = h_wspdf['pdfNBins'].Clone()
    h_wdata_ratio = h_wdata.Clone()
    h_wdata_ratio.Reset()
    for ibin in range(1,h_wdata.GetNbinsX()+1):
      bcenter = h_wdata.GetBinCenter(ibin)
      if(not opt.unblind)&(bcenter>blindingRegion[0])&(bcenter<blindingRegion[1]): continue
      wbval, wberr = h_wdata.GetBinContent(ibin), h_wdata.GetBinError(ibin)
      wbkgval = h_wbpdf['nBins'].GetBinContent(ibin)
      h_wdata_ratio.SetBinContent(ibin,wbval-wbkgval)
      h_wdata_ratio.SetBinError(ibin,wberr)

  # Sum histograms if processing multiple categories
  if( len(opt.cats.split(",")) > 1 )|( opt.cats == 'all' ):
    if opt.doSumCategories:
      print "    * adding histogram to sum"
      if cidx == 0:
	h_data_sum = h_data.Clone()
	h_data_ratio_sum = h_data_ratio.Clone()
	h_sbpdf_sum = {'pdfNBins':h_sbpdf['pdfNBins'].Clone(),'nBins':h_sbpdf['nBins'].Clone()}
	h_bpdf_sum = {'pdfNBins':h_bpdf['pdfNBins'].Clone(),'nBins':h_bpdf['nBins'].Clone()}
	h_bpdf_ratio_sum = h_bpdf_ratio.Clone()
	h_spdf_sum = {'pdfNBins':h_spdf['pdfNBins'].Clone(),'nBins':h_spdf['nBins'].Clone()}
	h_spdf_ratio_sum = h_spdf_ratio.Clone()
        if opt.doCatWeights:
	  h_wdata_sum = h_wdata.Clone()
	  h_wdata_ratio_sum = h_wdata_ratio.Clone()
	  h_wsbpdf_sum = {'pdfNBins':h_wsbpdf['pdfNBins'].Clone(),'nBins':h_wsbpdf['nBins'].Clone()}
	  h_wbpdf_sum = {'pdfNBins':h_wbpdf['pdfNBins'].Clone(),'nBins':h_wbpdf['nBins'].Clone()}
	  h_wbpdf_ratio_sum = h_wbpdf_ratio.Clone()
	  h_wspdf_sum = {'pdfNBins':h_wspdf['pdfNBins'].Clone(),'nBins':h_wspdf['nBins'].Clone()}
	  h_wspdf_ratio_sum = h_wspdf_ratio.Clone()
      else:
	h_data_sum += h_data.Clone()
	h_data_ratio_sum += h_data_ratio.Clone()
	for b,h in h_sbpdf.iteritems(): h_sbpdf_sum[b] += h.Clone()
	for b,h in h_bpdf.iteritems(): h_bpdf_sum[b] += h.Clone()
	h_bpdf_ratio_sum += h_bpdf_ratio.Clone()
	for b,h in h_spdf.iteritems(): h_spdf_sum[b] += h.Clone()
	h_spdf_ratio_sum += h_spdf_ratio.Clone()
        if opt.doCatWeights:
	  h_wdata_sum += h_wdata.Clone()
	  h_wdata_ratio_sum += h_wdata_ratio.Clone()
	  for b,h in h_wsbpdf.iteritems(): h_wsbpdf_sum[b] += h.Clone()
	  for b,h in h_wbpdf.iteritems(): h_wbpdf_sum[b] += h.Clone()
	  h_wbpdf_ratio_sum += h_wbpdf_ratio.Clone()
	  for b,h in h_wspdf.iteritems(): h_wspdf_sum[b] += h.Clone()
	  h_wspdf_ratio_sum += h_wspdf_ratio.Clone()

  # Make plot for individual cats
  if not opt.skipIndividualCatPlots:
    print "    * making plot"
    if not os.path.isdir("./SplusBModels%s"%(opt.ext)): os.system("mkdir ./SplusBModels%s"%(opt.ext))
    if opt.doBands: makeSplusBPlot(w,h_data,h_sbpdf,h_bpdf,h_spdf,h_data_ratio,h_bpdf_ratio,h_spdf_ratio,c,opt,df_bands,_reduceRange)
    else: makeSplusBPlot(w,h_data,h_sbpdf,h_bpdf,h_spdf,h_data_ratio,h_bpdf_ratio,h_spdf_ratio,c,opt,None,_reduceRange)

  # Delete histograms
  h_data.Delete()
  h_data_ratio.Delete()
  for h in h_sbpdf.itervalues(): h.Delete()
  for h in h_bpdf.itervalues(): h.Delete()
  h_bpdf_ratio.Delete()
  for h in h_spdf.itervalues(): h.Delete()
  h_spdf_ratio.Delete()
  if opt.doCatWeights:
    h_wdata.Delete()
    h_wdata_ratio.Delete()
    for h in h_wsbpdf.itervalues(): h.Delete()
    for h in h_wbpdf.itervalues(): h.Delete()
    h_wbpdf_ratio.Delete()
    for h in h_wspdf.itervalues(): h.Delete()
    h_wspdf_ratio.Delete()
  print "    * finished processing\n"

# Finished processing individual categories: if all then plot all
if( len(opt.cats.split(",")) > 1 )|( opt.cats == 'all' ):
  if opt.doHHMjjFix: _reduceRange = [xvarfix.getMin(),xvarfix.getMax()]
  else: _reduceRange = None
  if opt.doSumCategories:
    if not os.path.isdir("./SplusBModels%s"%(opt.ext)): os.system("mkdir ./SplusBModels%s"%(opt.ext))
    print " --> Making plot for sum of categories"
    if opt.doBands: makeSplusBPlot(w,h_data_sum,h_sbpdf_sum,h_bpdf_sum,h_spdf_sum,h_data_ratio_sum,h_bpdf_ratio_sum,h_spdf_ratio_sum,'all',opt, df_bands,_reduceRange)
    else: makeSplusBPlot(w,h_data_sum,h_sbpdf_sum,h_bpdf_sum,h_spdf_sum,h_data_ratio_sum,h_bpdf_ratio_sum,h_spdf_ratio_sum,'all',opt,None,_reduceRange)
    if opt.doCatWeights:
      print " --> Making weighted plot for sum of categories"
      if opt.doBands: makeSplusBPlot(w,h_wdata_sum,h_wsbpdf_sum,h_wbpdf_sum,h_wspdf_sum,h_wdata_ratio_sum,h_wbpdf_ratio_sum,h_wspdf_ratio_sum,'wall',opt, df_bands, _reduceRange)
      else: makeSplusBPlot(w,h_wdata_sum,h_wsbpdf_sum,h_wbpdf_sum,h_wspdf_sum,h_wdata_ratio_sum,h_wbpdf_ratio_sum,h_wspdf_ratio_sum,'wall',opt, None, _reduceRange)
