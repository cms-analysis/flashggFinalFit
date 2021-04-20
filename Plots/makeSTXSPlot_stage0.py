import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
import math
from collections import OrderedDict as od

def get_options():
  parser = OptionParser()
  parser.add_option("--inputJson", dest="inputJson", default='', help="Input json file with results")
  parser.add_option("--inputXSBRjson", dest="inputXSBRjson", default='', help="Input XSBR json file")
  parser.add_option("--mode", dest="mode", default='stage1p2_maximal', help="Mode: stage1p2_maximal or stage1p2_minimal")
  parser.add_option("--translatePOIs", dest="translatePOIs", default=None, help="JSON to store poi translations")
  parser.add_option("--doTHBox", dest="doTHBox", default=False, action="store_true", help="Do separate box for tH in ratio plot")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetHatchesLineWidth(1)
ROOT.gStyle.SetHatchesSpacing(1)
#ROOT.gStyle.SetEndErrorSize(7)

# Parameters of interest
params = od()
params['stage0'] = ['r_ggH', 'r_qqH', 'r_WH_lep', 'r_ZH_lep', 'r_ttH', 'r_tH']
params['stage1p2_maximal'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_VBFlike', 'r_ggH_BSM', 'r_qqH_VBFlike', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep', 'r_ZH_lep', 'r_ttH', 'r_tH']
params['stage1p2_minimal'] = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_BSM_low', 'r_ggH_BSM_high', 'r_qqH_low_mjj_low_pthjj', 'r_qqH_low_mjj_high_pthjj', 'r_qqH_high_mjj_low_pthjj', 'r_qqH_high_mjj_high_pthjj', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep_low', 'r_WH_lep_high', 'r_ZH_lep', 'r_ttH_low', 'r_ttH_medlow', 'r_ttH_medhigh', 'r_ttH_high', 'r_tH']

#Function to extract results from json
def CopyDataFromJsonFile(jsonfilename='observed.json', model=None, pois=[]):
  res = {}
  with open(jsonfilename) as jsonfile:
    full = json.load(jsonfile)[model]
    for poi in pois: res[poi] = dict(full[poi])
  return res

# Functions for translations
def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)

# Load values
results = CopyDataFromJsonFile(opt.inputJson,opt.mode,params[opt.mode])
with open(opt.inputXSBRjson,"r") as jsonfile: xsbr_theory = json.load(jsonfile)
translatePOIs = {} if opt.translatePOIs is None else LoadTranslations(opt.translatePOIs)
nPOIs = len(params[opt.mode])

# Color Map
colorMap = {'ggH':ROOT.kAzure+7,'qqH':ROOT.kOrange-3,'WH':ROOT.kGreen+2,'ZH':ROOT.kGreen+2,'ttH':ROOT.kPink+6,'tH':ROOT.kOrange}
colorMapSyst = {'ggH':ROOT.kAzure+6,'qqH':ROOT.kOrange-4,'WH':ROOT.kGreen-6,'ZH':ROOT.kGreen-6,'ttH':ROOT.kPink+1,'tH':ROOT.kYellow-9}
ROOT.gStyle.SetLineStyleString(2,"20 20")

# Make all graphs (nominal + ratio) for each production mode
grs_nominal = {}
grs_nominal_bf = {}
grs_nominal_systonly = {}
grs_nominal_theory = {}
grs_nominal_theory_v = {}
grs_ratio = {}
grs_ratio_bf = {}
grs_ratio_systonly = {}
grs_ratio_theory = {}
for pm in ['ggH','qqH','WH','ZH','ttH','tH']: 
  grs_nominal[pm] = ROOT.TGraphAsymmErrors()
  grs_nominal[pm].SetLineColor(colorMap[pm])
  grs_nominal[pm].SetFillColor(colorMap[pm])
  grs_nominal[pm].SetLineWidth(0)
  grs_nominal[pm].SetMarkerSize(0.2)
  grs_nominal[pm].SetMarkerStyle(25)
  grs_nominal[pm].SetMarkerColor(0)
  grs_nominal_bf[pm] = ROOT.TGraphAsymmErrors()
  grs_nominal_bf[pm].SetFillColor(0)
  grs_nominal_bf[pm].SetLineWidth(0)
  grs_nominal_bf[pm].SetMarkerSize(0)
  grs_nominal_systonly[pm] = ROOT.TGraphAsymmErrors()
  grs_nominal_systonly[pm].SetFillColor(colorMapSyst[pm])
  grs_nominal_systonly[pm].SetLineWidth(0)
  grs_nominal_systonly[pm].SetMarkerSize(0)
  grs_nominal_theory[pm] = ROOT.TGraphAsymmErrors()
  grs_nominal_theory[pm].SetLineWidth(0)
  grs_nominal_theory[pm].SetFillColor(17)
  grs_nominal_theory[pm].SetFillStyle(3144)
  grs_nominal_theory[pm].SetMarkerSize(0)
  grs_nominal_theory_v[pm] = ROOT.TGraphAsymmErrors()
  grs_nominal_theory_v[pm].SetLineWidth(1)
  grs_nominal_theory_v[pm].SetLineColor(14)
  grs_nominal_theory_v[pm].SetMarkerSize(0)
  grs_nominal_theory_v[pm].SetMarkerColor(14)

  grs_ratio[pm] = ROOT.TGraphAsymmErrors()
  grs_ratio[pm].SetLineColor(colorMap[pm])
  grs_ratio[pm].SetFillColor(colorMap[pm])
  grs_ratio[pm].SetLineWidth(2)
  grs_ratio[pm].SetMarkerSize(0.2)
  grs_ratio[pm].SetMarkerStyle(25)
  grs_ratio[pm].SetMarkerColor(0)
  grs_ratio_bf[pm] = ROOT.TGraphAsymmErrors()
  grs_ratio_bf[pm].SetFillColor(0)
  grs_ratio_bf[pm].SetLineWidth(0)
  grs_ratio_bf[pm].SetMarkerSize(0)
  grs_ratio_systonly[pm] = ROOT.TGraphAsymmErrors()
  grs_ratio_systonly[pm].SetFillColor(colorMapSyst[pm])
  grs_ratio_systonly[pm].SetLineWidth(0)
  grs_ratio_systonly[pm].SetMarkerSize(0)
  grs_ratio_theory[pm] = ROOT.TGraphAsymmErrors()
  grs_ratio_theory[pm].SetLineWidth(0)
  grs_ratio_theory[pm].SetFillColor(17)
  grs_ratio_theory[pm].SetFillStyle(3144)
  grs_ratio_theory[pm].SetMarkerSize(0)

if opt.doTHBox:
  grs_ratio_TH = ROOT.TGraphAsymmErrors()
  grs_ratio_TH.SetLineColor(colorMap['tH'])
  grs_ratio_TH.SetFillColor(colorMap['tH'])
  grs_ratio_TH.SetLineWidth(2)
  grs_ratio_TH.SetMarkerSize(0.2)
  grs_ratio_TH.SetMarkerStyle(25)
  grs_ratio_TH.SetMarkerColor(0)
  grs_ratio_bf_TH = ROOT.TGraphAsymmErrors()
  grs_ratio_bf_TH.SetFillColor(0)
  grs_ratio_bf_TH.SetLineWidth(0)
  grs_ratio_bf_TH.SetMarkerSize(0)
  grs_ratio_systonly_TH = ROOT.TGraphAsymmErrors()
  grs_ratio_systonly_TH.SetFillColor(colorMapSyst['tH'])
  grs_ratio_systonly_TH.SetLineWidth(0)
  grs_ratio_systonly_TH.SetMarkerSize(0)
  grs_ratio_theory_TH = ROOT.TGraphAsymmErrors()
  grs_ratio_theory_TH.SetLineWidth(0)
  grs_ratio_theory_TH.SetFillColor(17)
  grs_ratio_theory_TH.SetFillStyle(3144)
  grs_ratio_theory_TH.SetMarkerSize(0)

# If mininmal add dashed lines 
if "minimal" in opt.mode:
  grs_nominal_VBFlike = ROOT.TGraphAsymmErrors()
  grs_nominal_VBFlike.SetLineColor(colorMap["ggH"])
  grs_nominal_VBFlike.SetLineWidth(2)
  grs_nominal_VBFlike.SetLineStyle(2)
  grs_nominal_VBFlike.SetMarkerSize(0.2)
  grs_nominal_VBFlike.SetMarkerStyle(25)
  grs_nominal_VBFlike.SetMarkerColor(0)
  grs_ratio_VBFlike = ROOT.TGraphAsymmErrors()
  grs_ratio_VBFlike.SetLineColor(colorMap["ggH"])
  grs_ratio_VBFlike.SetLineWidth(2)
  grs_ratio_VBFlike.SetLineStyle(2)
  grs_ratio_VBFlike.SetMarkerSize(0.2)
  grs_ratio_VBFlike.SetMarkerStyle(25)
  grs_ratio_VBFlike.SetMarkerColor(0)

for poi_idx in range(len(params[opt.mode])):
  poi = params[opt.mode][poi_idx]
  xsbr = xsbr_theory[poi]['nominal']
  pm = poi.split("_")[1]
  grs_nominal[pm].SetPoint(grs_nominal[pm].GetN(),poi_idx+0.5,results[poi]['Val']*xsbr)
  grs_nominal[pm].SetPointError(grs_nominal[pm].GetN()-1,0.015,0.015,abs(results[poi]['ErrorLo']*xsbr),abs(results[poi]['ErrorHi']*xsbr))
  grs_nominal_systonly[pm].SetPoint(grs_nominal_systonly[pm].GetN(),poi_idx+0.5,results[poi]['Val']*xsbr)
  grs_nominal_systonly[pm].SetPointError(grs_nominal_systonly[pm].GetN()-1,0.15,0.15,abs(results[poi]['SystLo']*xsbr),abs(results[poi]['SystHi']*xsbr))
  grs_nominal_bf[pm].SetPoint(grs_nominal_bf[pm].GetN(),poi_idx+0.5,results[poi]['Val']*xsbr)
  grs_nominal_bf[pm].SetPointError(grs_nominal_bf[pm].GetN()-1,0.05,0.05,0.1*abs(results[poi]['SystLo']*xsbr),0.1*abs(results[poi]['SystHi']*xsbr))
  grs_nominal_theory[pm].SetPoint(grs_nominal_theory[pm].GetN(),poi_idx+0.5,xsbr)
  grs_nominal_theory[pm].SetPointError(grs_nominal_theory[pm].GetN()-1,0.35,0.35,xsbr_theory[poi]['Low01Sigma'],xsbr_theory[poi]['High01Sigma'])
  grs_nominal_theory_v[pm].SetPoint(grs_nominal_theory_v[pm].GetN(),poi_idx+0.5,xsbr)
  grs_nominal_theory_v[pm].SetPointError(grs_nominal_theory_v[pm].GetN()-1,0.35,0.35,0.001,0.001)

  if( poi == "r_tH")&( opt.doTHBox ):
    grs_ratio_TH.SetPoint(grs_ratio_TH.GetN(),poi_idx+0.5,0.25*results[poi]['Val'])
    grs_ratio_TH.SetPointError(grs_ratio_TH.GetN()-1,0.015,0.015,0.25*abs(results[poi]['ErrorLo']),0.25*abs(results[poi]['ErrorHi']))
    grs_ratio_systonly_TH.SetPoint(grs_ratio_systonly_TH.GetN(),poi_idx+0.5,0.25*results[poi]['Val'])
    grs_ratio_systonly_TH.SetPointError(grs_ratio_systonly_TH.GetN()-1,0.15,0.15,0.25*abs(results[poi]['SystLo']),0.25*abs(results[poi]['SystHi']))
    grs_ratio_bf_TH.SetPoint(grs_ratio_bf_TH.GetN(),poi_idx+0.5,0.25*results[poi]['Val'])
    grs_ratio_bf_TH.SetPointError(grs_ratio_bf_TH.GetN()-1,0.05,0.05,0.25*0.015,0.25*0.015)
    grs_ratio_theory_TH.SetPoint(grs_ratio_theory_TH.GetN(),poi_idx+0.5,0.25*1.0)
    grs_ratio_theory_TH.SetPointError(grs_ratio_theory_TH.GetN()-1,0.35,0.35,0.25*xsbr_theory[poi]['FracLow01Sigma'],0.25*xsbr_theory[poi]['FracHigh01Sigma'])
  else:
    grs_ratio[pm].SetPoint(grs_ratio[pm].GetN(),poi_idx+0.5,results[poi]['Val'])
    grs_ratio[pm].SetPointError(grs_ratio[pm].GetN()-1,0.015,0.015,abs(results[poi]['ErrorLo']),abs(results[poi]['ErrorHi']))
    grs_ratio_systonly[pm].SetPoint(grs_ratio_systonly[pm].GetN(),poi_idx+0.5,results[poi]['Val'])
    grs_ratio_systonly[pm].SetPointError(grs_ratio_systonly[pm].GetN()-1,0.15,0.15,abs(results[poi]['SystLo']),abs(results[poi]['SystHi']))
    grs_ratio_bf[pm].SetPoint(grs_ratio_bf[pm].GetN(),poi_idx+0.5,results[poi]['Val'])
    grs_ratio_bf[pm].SetPointError(grs_ratio_bf[pm].GetN()-1,0.05,0.05,0.015,0.015)
    grs_ratio_theory[pm].SetPoint(grs_ratio_theory[pm].GetN(),poi_idx+0.5,1.0)
    grs_ratio_theory[pm].SetPointError(grs_ratio_theory[pm].GetN()-1,0.35,0.35,xsbr_theory[poi]['FracLow01Sigma'],xsbr_theory[poi]['FracHigh01Sigma'])

  if "minimal" in opt.mode:
    if poi in ['r_qqH_low_mjj_low_pthjj','r_qqH_low_mjj_high_pthjj','r_qqH_high_mjj_low_pthjj','r_qqH_high_mjj_high_pthjj']:
      grs_nominal_VBFlike.SetPoint(grs_nominal_VBFlike.GetN(),poi_idx+0.5,results[poi]['Val']*xsbr)
      grs_nominal_VBFlike.SetPointError(grs_nominal_VBFlike.GetN()-1,0,0,abs(results[poi]['ErrorLo']*xsbr),abs(results[poi]['ErrorHi']*xsbr))
      grs_nominal_VBFlike.SetPointError(grs_nominal_VBFlike.GetN()-1,0,0,abs(results[poi]['ErrorLo']*xsbr),abs(results[poi]['ErrorHi']*xsbr))
      grs_ratio_VBFlike.SetPoint(grs_ratio_VBFlike.GetN(),poi_idx+0.5,results[poi]['Val'])
      grs_ratio_VBFlike.SetPointError(grs_ratio_VBFlike.GetN()-1,0,0,abs(results[poi]['ErrorLo']),abs(results[poi]['ErrorHi']))


# Get maximum and min values
nominal_max, nominal_min = 0, 999
ratio_max = 0
for gr in grs_nominal.itervalues():
  if max(gr.GetY()) > nominal_max: nominal_max = max(gr.GetY())
  if min(gr.GetY()) < nominal_min: nominal_min = min(gr.GetY())
for mode, gr in grs_ratio.iteritems():
  if mode == "tH": continue
  if max(gr.GetY()) > ratio_max: ratio_max = max(gr.GetY())

# Create canvas
canv = ROOT.TCanvas("canv","canv",1000,900)
pad1 = ROOT.TPad("pad1","pad1",0,0.25,1,1)
pad1.SetTickx()
pad1.SetTicky()
pad1.SetLogy()
pad1.SetTopMargin(0.14)
pad1.SetBottomMargin(0.18)
#pad1.SetBottomMargin(0.28)
pad1.Draw()
pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.37)
pad2.SetTickx()
pad2.SetTicky()
pad2.SetTopMargin(0.000001)
pad2.SetBottomMargin(0.2)
pad2.Draw()
padSizeRatio = 0.75/0.37

# FUnction to extract label string
def extractLabelStr(p,res,theory):
  lstr = ""
  x = res[p]['Val']*theory[p]['nominal']
  u_up = res[p]['ErrorHi']*theory[p]['nominal']
  u_down = res[p]['ErrorLo']*theory[p]['nominal']
  if x >= 9.95: lstr += "%.0f^{#plus%.0f}_{#minus%.0f}"%(x,abs(u_up),abs(u_down))
  elif x >= 1.: lstr += "%.1f^{#plus%.1f}_{#minus%.1f}"%(x,abs(u_up),abs(u_down))
  else: lstr += "%.2f^{#plus%.2f}_{#minus%.2f}"%(x,abs(u_up),abs(u_down))
  return lstr 

# Draw graphs
pad1.cd()
haxes = ROOT.TH1F("haxes","",nPOIs,0,nPOIs)
#for bidx in range(1,haxes.GetNbinsX()+1):
#  poi = params[opt.mode][bidx-1]
#  label_str = extractLabelStr(poi,results,xsbr_theory)
#  haxes.GetXaxis().SetBinLabel(bidx,"%s"%label_str)
#haxes.GetXaxis().SetLabelSize(0.045)
haxes.GetXaxis().SetLabelSize(0)
#haxes.GetXaxis().LabelsOption("v")
haxes.GetXaxis().SetTickSize(0)
haxes.GetYaxis().SetLabelSize(0.04)
haxes.GetYaxis().SetTitle("#sigma_{obs} #bf{#it{#Beta}} [fb]")
haxes.GetYaxis().SetTitleSize(0.06)
haxes.GetYaxis().SetTitleOffset(0.7)
haxes.SetMaximum(nominal_max*5)
haxes.SetMinimum(nominal_min*0.1)
haxes.SetLineWidth(0)
haxes.Draw()
# Vertical lines for each poi
vlines = {}
for i in range(1,nPOIs):
  vlines['vline_%g'%i] = ROOT.TLine(i,haxes.GetMinimum(),i,haxes.GetMaximum())
  vlines['vline_%g'%i].SetLineColorAlpha(ROOT.kGray,0.5)
  vlines['vline_%g'%i].Draw("SAME")
for gr in grs_nominal_theory.itervalues(): gr.Draw("SAME E2")
for gr in grs_nominal_theory_v.itervalues(): gr.Draw("SAME PE")
for gr in grs_nominal_systonly.itervalues(): gr.Draw("SAME E2")
for gr in grs_nominal.itervalues(): gr.Draw("SAME E2P")
if "minimal" in opt.mode: grs_nominal_VBFlike.Draw("SAME ZP")
#for gr in grs_nominal_bf.itervalues(): gr.Draw("SAME E2")
# Add legend
leg = ROOT.TLegend(0.52,0.55,0.87,0.85)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetLineColor(0)
leg.SetLineWidth(0)
leg.SetTextSize(0.04)
gr_bf_dummy = ROOT.TGraph()
gr_bf_dummy.SetMarkerSize(1)
gr_bf_dummy.SetMarkerStyle(25)
if "obs" in opt.inputJson: leg.AddEntry(gr_bf_dummy,"Observed","P")
else: leg.AddEntry(gr_bf_dummy,"Expected","P")
gr_dummy_statsyst = ROOT.TGraph()
gr_dummy_statsyst.SetLineColor(ROOT.kBlack)
gr_dummy_statsyst.SetLineWidth(2)
leg.AddEntry(gr_dummy_statsyst,"#pm1#sigma (stat #oplus syst)","E")
gr_dummy = ROOT.TGraph()
gr_dummy.SetLineColor(ROOT.kBlack)
gr_dummy.SetMarkerStyle(21)
gr_dummy.SetMarkerSize(2.5)
gr_dummy.SetMarkerColor(ROOT.kBlack)
gr_dummy.SetLineWidth(2)
leg.AddEntry(gr_dummy,"#pm1#sigma (syst)","P")
gr_theory_dummy = ROOT.TGraph()
gr_theory_dummy.SetLineWidth(0)
gr_theory_dummy.SetFillColor(17)
gr_theory_dummy.SetFillStyle(3144)
leg.AddEntry(gr_theory_dummy,"SM prediction","F")
leg.Draw("SAME")
# Add box for values
#vBox = ROOT.TBox(0.03 ,105 ,0.5,nominal_max*9.3 )
#vBox2 = ROOT.TBox(nPOIs-0.5,105 ,nPOIs-0.03,nominal_max*9.3 )
#vBox.SetFillColor(0)
#vBox2.SetFillColor(0)
#vBox.Draw("Same")
#vBox2.Draw("Same")
# Add numbers
lat1 = ROOT.TLatex()
lat1.SetTextFont(42)
lat1.SetTextAlign(21)
boxes = {}
#lat1.SetNDC()
if "maximal" in opt.mode: lat1.SetTextSize(0.032)
elif "stage0" in opt.mode: lat1.SetTextSize(0.035)
else: lat1.SetTextSize(0.024)
for bidx in range(1,haxes.GetNbinsX()+1):
  poi = params[opt.mode][bidx-1]
  label_str = extractLabelStr(poi,results,xsbr_theory)
  xval = haxes.GetXaxis().GetBinCenter(bidx)
  #xval = 0.1+(0.9-0.1)*(haxes.GetXaxis().GetBinCenter(bidx)/nPOIs)
  yval = max((results[poi]['Val']+1.5*results[poi]['ErrorHi'])*xsbr_theory[poi]['nominal'],xsbr_theory[poi]['nominal']+3*xsbr_theory[poi]['High01Sigma'])
  #yval = 0.82 
  # Add box to outmost columns
  if bidx in [1,haxes.GetNbinsX()]:
    boxes["b%g"%bidx] = ROOT.TBox(xval-0.37,yval*0.8,xval+0.42,yval*1.4)
    boxes["b%g"%bidx].SetFillColor(0)
    #boxes["b%g"%bidx].Draw("Same")

  lat1.DrawLatex(xval,yval,label_str)
    

lat2 = ROOT.TLatex()
lat2.SetTextFont(42)
lat2.SetTextAlign(11)
lat2.SetNDC()
lat2.SetTextSize(0.032)
lat2.DrawLatex(0.15,0.39,"H #rightarrow #gamma#gamma, |y_{H}| < 2.5")
if "minimal" in opt.mode: 
  lat2.DrawLatex(0.13,0.32,"STXS stage 1.2: minimal")
  if "obs" in opt.inputJson: lat2.DrawLatex(0.13,0.25,"m_{H} = 125.38 GeV,  #it{p}_{SM} = 85%")
  else: lat2.DrawLatex(0.13,0.25,"m_{H} = 125.38 GeV")
elif "maximal" in opt.mode: 
  lat2.DrawLatex(0.13,0.32,"STXS stage 1.2: maximal")
  if "obs" in opt.inputJson: lat2.DrawLatex(0.13,0.25,"m_{H} = 125.38 GeV,  #it{p}_{SM} = 62%")
  else: lat2.DrawLatex(0.13,0.25,"m_{H} = 125.38 GeV")
elif "stage0" in opt.mode:
  lat2.DrawLatex(0.15,0.32,"STXS stage 0")
  if "obs" in opt.inputJson: lat2.DrawLatex(0.15,0.25,"m_{H} = 125.38 GeV,  #it{p}_{SM} = 35%")
  else: lat2.DrawLatex(0.13,0.25,"m_{H} = 125.38 GeV")

#if "obs" in opt.inputJson: lat1.DrawLatex(0.13,0.8,"H#rightarrow#gamma#gamma")
#else: lat1.DrawLatex(0.13,0.8,"H#rightarrow#gamma#gamma, m_{H} = 125.0 GeV")

# Ratio plot
pad2.cd()
haxes_r = ROOT.TH1F("haxes_r","",nPOIs,0,nPOIs)
for bidx in range(1,haxes_r.GetNbinsX()+1): haxes_r.GetXaxis().SetBinLabel(bidx,Translate(params[opt.mode][bidx-1],translatePOIs))
if opt.mode == "stage1p2_minimal": haxes_r.GetXaxis().SetLabelSize(0.045*padSizeRatio)
elif opt.mode == "stage1p2_maximal": haxes_r.GetXaxis().SetLabelSize(0.06*padSizeRatio)
else: haxes_r.GetXaxis().SetLabelSize(0.07*padSizeRatio)
haxes_r.GetXaxis().SetTickSize(0)
haxes_r.GetXaxis().SetLabelOffset(0.02)
haxes_r.GetXaxis().LabelsOption("h")
haxes_r.GetYaxis().SetLabelSize(0.04*padSizeRatio)
haxes_r.GetYaxis().SetTitle("Ratio to SM")
haxes_r.GetYaxis().SetTitleSize(0.06*padSizeRatio)
haxes_r.GetYaxis().SetTitleOffset(0.7/padSizeRatio)
haxes_r.GetYaxis().CenterTitle()
if 'expected' in opt.inputJson: haxes_r.SetMaximum(5)
#else: haxes_r.SetMaximum(ratio_max)
else: haxes_r.SetMaximum(2.9)
#else: haxes_r.SetMaximum(ratio_max*2)
#else: haxes_r.SetMaximum(10)
haxes_r.SetMinimum(-0.49)
haxes_r.SetLineWidth(0)
haxes_r.Draw()
if opt.doTHBox:
  THBox = ROOT.TBox(nPOIs-1,-0.48,nPOIs,2.87)
  THBox.SetFillStyle(1001)
  THBox.SetFillColor(ROOT.kWhite)
  THBox.Draw("SAME")

if opt.doTHBox:
  # Make axis for RHS
  axis_TH = ROOT.TGaxis(nPOIs,-0.49,nPOIs,2.9,-0.49*4, 2.9*4, 610, "+L")
  axis_TH.SetLabelSize(0.04*padSizeRatio)
  axis_TH.SetLabelFont(42)
  axis_TH.SetTickLength(0.0)
  axis_TH.Draw("Same")



# Vertical lines for each poi
for i in range(1,nPOIs):
  vlines['vline_r_%g'%i] = ROOT.TLine(i,haxes_r.GetMinimum(),i,haxes_r.GetMaximum())
  if( opt.doTHBox )&( i == (nPOIs-1) ): vlines['vline_r_%g'%i].SetLineColor(1)
  else:vlines['vline_r_%g'%i].SetLineColorAlpha(ROOT.kGray,0.5)
  vlines['vline_r_%g'%i].Draw("SAME")

hlines = {}
yvals = [0.5,0.75,1,1.25,1.5,2.,4.]
for i in range(len(yvals)):
  yval = yvals[i]
  if opt.doTHBox: hlines['hline_%g'%i] = ROOT.TLine(0,yval,nPOIs-1,yval)
  else: hlines['hline_%g'%i] = ROOT.TLine(0,yval,nPOIs,yval)
  if yval != 1: hlines['hline_%g'%i].SetLineColorAlpha(ROOT.kGray,0.5)
  hlines['hline_%g'%i].SetLineStyle(2)
  hlines['hline_%g'%i].Draw("SAME")

yvals = [0.5,0.75,1,1.25,1.5,2.,4.,8.]
if opt.doTHBox:
  for i in range(len(yvals)):
    yval = yvals[i]
    hlines['hline_TH_%g'%i] = ROOT.TLine(nPOIs-1,yval*0.25,nPOIs,yval*0.25)
    if yval != 1.: hlines['hline_TH_%g'%i].SetLineColorAlpha(ROOT.kGray,0.5)
    hlines['hline_TH_%g'%i].SetLineStyle(2)
    hlines['hline_TH_%g'%i].Draw("SAME")

   
# Draw graphs
for gr in grs_ratio_theory.itervalues(): gr.Draw("SAME E2")
for gr in grs_ratio_systonly.itervalues(): gr.Draw("SAME E2")
for gr in grs_ratio.itervalues(): gr.Draw("SAME E2P")
if "minimal" in opt.mode: grs_ratio_VBFlike.Draw("SAME ZP")
if opt.doTHBox:
  grs_ratio_theory_TH.Draw("SAME E2")
  grs_ratio_systonly_TH.Draw("SAME E2")
  grs_ratio_TH.Draw("SAME ZP")

# Draw hatched box
line_0 = ROOT.TLine(0,-0.02,nPOIs,-0.02)
line_0.SetLineWidth(2)
line_0.Draw("SAME")
hatchBox = ROOT.TBox(0,-0.3,nPOIs,0)
hatchBox.SetFillStyle(3004)
hatchBox.SetFillColor(ROOT.kBlack)
hatchBox.Draw("SAME")


canv.cd()
lat = ROOT.TLatex()
lat.SetTextFont(42)
lat.SetTextAlign(11)
lat.SetNDC()
lat.SetTextSize(0.045)
#lat.DrawLatex(0.1,0.92,"#bf{CMS} #it{Preliminary}")
lat.DrawLatex(0.1,0.92,"#bf{CMS}")
lat3 = ROOT.TLatex()
lat3.SetTextFont(42)
lat3.SetTextAlign(31)
lat3.SetNDC()
lat3.SetTextSize(0.045)
lat3.DrawLatex(0.9,0.92,"137 fb^{-1} (13 TeV)")

# Save canvas
if "obs" in opt.inputJson:
  canv.SaveAs("/eos/home-j/jlangfor/www/CMS/thesis/chapter6/final/stxs_summary_%s_obs.pdf"%opt.mode)
  canv.SaveAs("/eos/home-j/jlangfor/www/CMS/thesis/chapter6/final/stxs_summary_%s_obs.png"%opt.mode)
else:
  canv.SaveAs("/eos/home-j/jlangfor/www/CMS/hgg/stxs_runII/Dec20/final_new/checks/results/stxs_summary_%s_exp.pdf"%opt.mode)
  canv.SaveAs("/eos/home-j/jlangfor/www/CMS/hgg/stxs_runII/Dec20/final_new/checks/results/stxs_summary_%s_exp.png"%opt.mode)



