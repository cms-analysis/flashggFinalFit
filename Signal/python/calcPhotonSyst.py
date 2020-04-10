# New script to calculate photon systematics
# * Per category
# * Output is pandas dataframe. Use extactPhotonSyst.py script to convert into .dat file to be read in SignalFit.cpp
# * Procs are read from list of files in inputWSDir

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PHOTON SYST CALCULATOR ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import ROOT
import pandas as pd
import pickle
import os, sys
from optparse import OptionParser
import glob
import re

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG PHOTON SYST CALCULATOR (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--inputWSDir", dest='inputWSDir', default='', help="Input flashgg WS directory")
  parser.add_option("--scales", dest='scales', default='', help="Photon shape systematics: scales")
  parser.add_option("--scalesCorr", dest='scalesCorr', default='', help='Photon shape systematics: scalesCorr')
  parser.add_option("--scalesGlobal", dest='scalesGlobal', default='', help='Photon shape systematics: scalesGlobal')
  parser.add_option("--smears", dest='smears', default='', help='Photon shape systematics: smears')
  parser.add_option("--nBins", dest='nBins', default=80, type='int', help='Number of bins in histograms')
  parser.add_option("--thresholdMean", dest='thresholdMean', default=0.05, type='float', help='Reject mean variations if larger than thresholdMean')
  parser.add_option("--thresholdSigma", dest='thresholdSigma', default=0.5, type='float', help='Reject mean variations if larger than thresholdSigma')
  parser.add_option("--thresholdRate", dest='thresholdRate', default=0.05, type='float', help='Reject mean variations if larger than thresholdRate')
  return parser.parse_args()
(opt,args) = get_options()

# Dictionary to store additional string for each syst type
inExtSyst = {'scales':'MCScale','scalesCorr':'','smears':'MCSmear'}
outExtSyst = {'scales':'13TeVscale','scalesCorr':'scale','smears':'13TeVsmear','scalesGlobal':'13TeVscale'}
# Function for converting STXS process to production mode in dataset name
def procToData( _proc ):
  proc_map = {"GG2H":"ggh","VBF":"vbf","WH2HQQ":"wh","ZH2HQQ":"zh","QQ2HLNU":"wh","QQ2HLL":"zh","TTH":"tth","BBH":"bbH","THQ":"thq","THW":"thw","TH":"thq"}
  for key in proc_map: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

# RooRealVar to fill histograms
mgg = ROOT.RooRealVar("CMS_hgg_mass","CMS_hgg_mass",125)

# Function to extact histograms from WS
def getHistograms( _ws, _nominalDataName, _sname ):
  _hists = {}
  # Define histograms
  for htype in ['nominal','up','down']:
    if htype == 'nominal': _hists[htype] = ROOT.TH1F(htype,htype,opt.nBins,100,180)
    else: _hists[htype] = ROOT.TH1F("%s_%s"%(_sname,htype),"%s_%s"%(_sname,htype),opt.nBins,100,180)
  # Extract nominal RooDataSet and syst RooDataHists
  rds_nominal = _ws.data(_nominalDataName)
  rdh_up = _ws.data("%s_%sUp01sigma"%(_nominalDataName,_sname))
  rdh_down = _ws.data("%s_%sDown01sigma"%(_nominalDataName,_sname))
  # Check if not NONE type and fill histograms
  if rds_nominal: rds_nominal.fillHistogram(_hists['nominal'],ROOT.RooArgList(mgg))
  else:
    print " --> [ERROR] Could not extract nominal RooDataSet: %s. Leaving"%_nominalDataName
    sys,exit(1)
  if rdh_up: rdh_up.fillHistogram(_hists['up'],ROOT.RooArgList(mgg))
  else:
    print " --> [ERROR] Could not extract RooDataHist (%s,up) for %s. Leaving"%(_sname,_nominalDataName)
    sys,exit(1)
  if rdh_down: rdh_down.fillHistogram(_hists['down'],ROOT.RooArgList(mgg))
  else:
    print " --> [ERROR] Could not extract RooDataHist (%s,down) for %s. Leaving"%(_sname,_nominalDataName)
    sys,exit(1) 
  return _hists

# Function to extract the sigma effective of a histogram
def effSigma(_h):
  nbins, binw, xmin = _h.GetXaxis().GetNbins(), _h.GetXaxis().GetBinWidth(1), _h.GetXaxis().GetXmin()
  mu, rms, total = _h.GetMean(), _h.GetRMS(), _h.Integral()
  # Scan round window of mean: window RMS/binWidth (cannot be bigger than 0.1*number of bins)
  nWindow = int(rms/binw) if (rms/binw) < 0.1*nbins else int(0.1*nbins)
  # Determine minimum width of distribution which holds 0.693 of total
  rlim = 0.683*total
  wmin, iscanmin = 9999999, -999
  for iscan in range(-1*nWindow,nWindow+1):
    # Find bin idx in scan: iscan from mean
    i_centre = int((mu-xmin)/binw+1+iscan)
    x_centre = (i_centre-0.5)*binw+xmin # * 0.5 for bin centre
    x_up, x_down = x_centre, x_centre
    i_up, i_down = i_centre, i_centre
    # Define counter for yield in bins: stop when counter > rlim
    y = _h.GetBinContent(i_centre) # Central bin height
    r = y
    reachedLimit = False
    for j in range(1,nbins):
      if reachedLimit: continue
      # Up:
      if(i_up < nbins)&(not reachedLimit):
        i_up+=1
        x_up+=binw
        y = _h.GetBinContent(i_up) # Current bin height
        r+=y
        if r>rlim: reachedLimit = True
      else: 
        print " --> Reach nBins in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName()
        return 0
      # Down:
      if( not reachedLimit ):
	if(i_down > 0):
	  i_down-=1
	  x_down-=binw
          y = _h.GetBinContent(i_down) #Current bin height
	  r+=y
	  if r>rlim: reachedLimit = True
	else:
	  print " --> Reach 0 in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName()
	  return 0
    # Calculate fractional width in bin takes above limt (assume linear)
    if y == 0.: dx = 0.
    else: dx = (r-rlim)*(binw/y)
    # Total width: half of peak
    w = (x_up-x_down+binw-dx)*0.5
    if w < wmin: 
      wmin = w
      iscanmin = iscan
  # Return effSigma
  return wmin  

# Functions to extract mean, sigma and rate variations
def getMeanVar(_hists):
  mu, muVar = {}, {}
  for htype,h in _hists.iteritems(): mu[htype] = h.GetMean()
  if mu['nominal']==0: return 0
  for htype in ['up','down']: muVar[htype] = (mu[htype]-mu['nominal'])/mu['nominal']
  x = (abs(muVar['up'])+abs(muVar['down']))/2
  # Check for NaN
  if x!=x: return 0
  else: return min(x,opt.thresholdMean)

def getSigmaVar(_hists):
  sigma, sigmaVar = {}, {}
  for htype,h in _hists.iteritems(): sigma[htype] = effSigma(h)
  if sigma['nominal']==0: return 0
  for htype in ['up','down']: sigmaVar[htype] = (sigma[htype]-sigma['nominal'])/sigma['nominal']
  x = (abs(sigmaVar['up'])+abs(sigmaVar['down']))/2
  if x!=x: return 0
  else: return min(x,opt.thresholdSigma)

def getRateVar(_hists):
  rate, rateVar = {}, {}
  for htype,h in _hists.iteritems(): rate[htype] = h.Integral()
  if rate['nominal']==0: return 0
  for htype in ['up','down']: rateVar[htype] = (rate[htype]-rate['nominal'])/rate['nominal']
  x = (abs(rateVar['up'])+abs(rateVar['down']))/2
  if x!=x: return 0
  else: return min(x,opt.thresholdRate)

# Define dataFrame
columns_data = ['proc','cat','inputWSFile','nominalDataName']
for stype in ['scales','scalesCorr','smears']:
  systs = getattr( opt, stype )
  for s in systs.split(","):
    if s == '': continue
    for x in ['mean','sigma','rate']: columns_data.append("%s_%s_%s"%(s,outExtSyst[stype],x))
data = pd.DataFrame( columns=columns_data ) 

# Extract processes from input WS dir
print " --> Taking signal workspaces from %s"%opt.inputWSDir
if not os.path.isdir( opt.inputWSDir ):
  print " --> [ERROR] Directory %s does not exist. Leaving"%opt.inputWSDir
  leave()
# Glob M125 worksapces
ws_fnames = glob.glob("%s/output*M125*"%opt.inputWSDir)
for fname in ws_fnames:
  # Extract process name
  _proc = re.sub(".root","",fname.split("pythia8_")[-1])
  _nominalDataName = "%s_125_13TeV_%s"%(procToData(_proc.split("_")[0]),opt.cat)
  data = data.append({'proc':_proc,'cat':opt.cat,'inputWSFile':fname,'nominalDataName':_nominalDataName}, ignore_index=True, sort=False)

# Loop over rows in dataFrame and open ws
for ir,r in data.iterrows():

  print " --> Processing (%s,%s)"%(r['proc'],opt.cat)

  # Open ROOT file and extract workspace
  f = ROOT.TFile(r['inputWSFile'])
  inputWS = f.Get("tagsDumper/cms_hgg_13TeV")
 
  # Loop over scale and smear systematics
  for stype in ['scales','scalesCorr','smears']:
    for s in getattr(opt,stype).split(","):
      if s == '': continue
      sname = "%s%s"%(inExtSyst[stype],s)
      #print "    * Systematic = %s (%s)"%(sname,stype)
      hists = getHistograms(inputWS,r['nominalDataName'],sname)
      # If nominal yield = 0:
      if hists['nominal'].Integral() == 0: _meanVar, _sigmaVar, _rateVar = 0, 0, 0
      else:
	_meanVar = getMeanVar(hists)
	_sigmaVar = getSigmaVar(hists)
	_rateVar = getRateVar(hists)
      # Add values to dataFrame
      data.at[ir,'%s_%s_mean'%(s,outExtSyst[stype])] = _meanVar
      data.at[ir,'%s_%s_sigma'%(s,outExtSyst[stype])] = _sigmaVar
      data.at[ir,'%s_%s_rate'%(s,outExtSyst[stype])] = _rateVar

      # Delete histograms
      for h in hists.itervalues(): h.Delete()

  # Delete ws and close file
  inputWS.Delete()
  f.Close()

# Output dataFrame as pickle file
if not os.path.isdir("./outdir_%s"%opt.ext): os.system("mkdir ./outdir_%s"%opt.ext)
if not os.path.isdir("./outdir_%s/calcPhotonSyst"%opt.ext): os.system("mkdir ./outdir_%s/calcPhotonSyst"%opt.ext)
if not os.path.isdir("./outdir_%s/calcPhotonSyst/pkl"%opt.ext): os.system("mkdir ./outdir_%s/calcPhotonSyst/pkl"%opt.ext)
with open("./outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(opt.ext,opt.cat),"wb") as f: pickle.dump(data,f) 
print " --> Successfully saved photon systematics as pkl file: ./outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(opt.ext,opt.cat)
