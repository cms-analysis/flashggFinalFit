# Script to make migration + purity matrices and output yields table
#  * Read in PANDAS dataframe

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from array import array
import glob
import pickle
import math
import json
from collections import OrderedDict
# Scripts for plotting
from plottingTools import getEffSigma, makeSplusBPlot
from shanePalette import set_color_palette

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG 2D PLOTTER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG 2D PLOTTER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLineStyleString(2,"4 10")

def get_options():
  parser = OptionParser()
  parser.add_option("--inputTreeFile", dest="inputTreeFile", default=None, help="Input ROOT tree")  
  parser.add_option("--xparam", dest="xparam", default="kappa_V:0.4,1.25", help="X-parameter:range")
  parser.add_option("--yparam", dest="yparam", default="kappa_F:-1.5,2.5", help="Y-parameter:range")
  parser.add_option("--nPoints", dest="nPoints", default=1000, type='int', help="N bins")
  parser.add_option("--nBins", dest="nBins", default=200, type='int', help="N bins")
  parser.add_option("--interpolation", dest="interpolation", default='linear', help="Interpolation")
  parser.add_option("--translatePOIs", dest="translatePOIs", default=None, help="JSON to store poi translations")
  parser.add_option("--doShift", dest="doShift", default=False, action="store_true", help="Shift minimum to 0")
  parser.add_option("--doBestFit", dest="doBestFit", default=False, action="store_true", help="Do best fit point")
  parser.add_option("--doSM", dest="doSM", default=False, action="store_true", help="Do SM point")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--placeLegend", dest="placeLegend", default='bottom_right', help="Legend position")
  parser.add_option("--no_colour", dest="no_colour", default=False, action="store_true", help="Legend position")
  return parser.parse_args()
(opt,args) = get_options()

# Set palette
if opt.no_colour: set_color_palette('boring')
else: set_color_palette('jonno_flip')

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translatePOIs = {} if opt.translatePOIs is None else LoadTranslations(opt.translatePOIs)

# Extract params and ranges
x, x_range = opt.xparam.split(":")[0], [float(opt.xparam.split(":")[1].split(",")[0]),float(opt.xparam.split(":")[1].split(",")[1])]
y, y_range = opt.yparam.split(":")[0], [float(opt.yparam.split(":")[1].split(",")[0]),float(opt.yparam.split(":")[1].split(",")[1])]

# Open tree and extract points and deltaNLL values
f_in = ROOT.TFile( opt.inputTreeFile )
t_in = f_in.Get("limit")
xvals, yvals, deltaNLL = [], [], []
ev_idx = 0
for ev in t_in:
  xvals.append( getattr(ev,x) )
  yvals.append( getattr(ev,y) )
  deltaNLL.append( getattr(ev,"deltaNLL") )

# Convert to numpy arrays as required for interpolation
dnll = np.asarray(deltaNLL)
points = np.array([xvals,yvals]).transpose()
# Set up grid
grid_x, grid_y = np.mgrid[x_range[0]:x_range[1]:opt.nPoints*1j, y_range[0]:y_range[1]:opt.nPoints*1j]
grid_vals = griddata(points,dnll,(grid_x,grid_y), method=opt.interpolation)

# Remove NANS
grid_x = grid_x[grid_vals==grid_vals]
grid_y = grid_y[grid_vals==grid_vals]
grid_vals = grid_vals[grid_vals==grid_vals]

min_val = np.min(grid_vals)

# Define Profile2D histogram
h2D = ROOT.TProfile2D("h","h",opt.nBins,x_range[0],x_range[1],opt.nBins,y_range[0],y_range[1])
for i in range(len(grid_vals)):
  if opt.doShift: h2D.Fill( grid_x[i], grid_y[i], 2*(grid_vals[i]-min_val) )
  else: h2D.Fill( grid_x[i], grid_y[i], 2*grid_vals[i] )

# Loop over bins: if content = 0 then set 999
for ibin in range(1,h2D.GetNbinsX()+1):
  for jbin in range(1,h2D.GetNbinsY()+1):
    if h2D.GetBinContent(ibin,jbin)==0: 
      xc, yc = h2D.GetXaxis().GetBinCenter(ibin), h2D.GetYaxis().GetBinCenter(jbin)
      h2D.Fill(xc,yc,999)

# Set up canvas
canv = ROOT.TCanvas("canv","canv",600,600)
canv.SetTickx()
canv.SetTicky()
if not opt.no_colour: canv.SetRightMargin(0.15)
canv.SetLeftMargin(0.115)
canv.SetBottomMargin(0.115)
# Extract binwidth
xw = (x_range[1]-x_range[0])/opt.nBins
yw = (y_range[1]-y_range[0])/opt.nBins
# Set histogram properties
h2D.SetContour(999)
h2D.SetTitle("")
h2D.GetXaxis().SetTitle(Translate(x,translatePOIs))
h2D.GetXaxis().SetTitleSize(0.05)
h2D.GetXaxis().SetTitleOffset(0.9)
h2D.GetXaxis().SetRangeUser(x_range[0]+xw,x_range[1]-xw)
h2D.GetYaxis().SetTitle(Translate(y,translatePOIs))
h2D.GetYaxis().SetTitleSize(0.05)
h2D.GetYaxis().SetTitleOffset(0.9)
h2D.GetYaxis().SetRangeUser(y_range[0]+yw,y_range[1]-yw)
#h2D.GetZaxis().SetTitle("-2 #Delta ln L")
h2D.GetZaxis().SetTitle("q(%s,%s)"%(Translate(x,translatePOIs),Translate(y,translatePOIs)))
h2D.GetZaxis().SetTitleSize(0.05)
h2D.GetZaxis().SetTitleOffset(0.8)
#h2D.SetMaximum(10)
h2D.SetMaximum(25)
# Make CI contours
c68, c95 = h2D.Clone(), h2D.Clone()
c68.SetContour(2)
c68.SetContourLevel(1,2.3)
c68.SetLineWidth(3)
c68.SetLineColor(ROOT.kBlack)
c95.SetContour(2)
c95.SetContourLevel(1,5.99)
c95.SetLineWidth(3)
c95.SetLineStyle(2)
c95.SetLineColor(ROOT.kBlack)
# Draw histogram and contours
if opt.no_colour: h2D.Draw("COL")
else: h2D.Draw("COLZ")
c68.Draw("cont3same")
c95.Draw("cont3same")
# Make best fit and sm points
if opt.doBestFit:
  gBF = ROOT.TGraph()
  gBF.SetPoint(0,grid_x[np.argmin(grid_vals)],grid_y[np.argmin(grid_vals)])
  gBF.SetMarkerStyle(34)
  gBF.SetMarkerSize(2)
  gBF.SetMarkerColor(ROOT.kBlack)
  gBF.Draw("P")
if opt.doSM:
  gSM = ROOT.TGraph()
  gSM.SetPoint(0,1,1)
  gSM.SetMarkerStyle(33)
  gSM.SetMarkerSize(2)
  gSM.SetMarkerColor(ROOT.kRed)
  gSM.Draw("P")

# Add plot info
lat = ROOT.TLatex()
lat.SetTextFont(42)
lat.SetLineWidth(2)
lat.SetTextAlign(11)
lat.SetNDC()
lat.SetTextSize(0.042)
#lat.DrawLatex(0.115,0.92,"#bf{CMS} #it{Preliminary}")
lat.DrawLatex(0.115,0.92,"#bf{CMS}")
lat.DrawLatex(0.62,0.92,"137 fb^{-1} (13#scale[0.75]{ }TeV)")
if "kappa_gam" in opt.inputTreeFile: lat.DrawLatex(0.17,0.2,"#scale[0.7]{H #rightarrow #gamma#gamma, m_{H} = 125.38 GeV}")
else: lat.DrawLatex(0.17,0.8,"#scale[0.7]{H #rightarrow #gamma#gamma, m_{H} = 125.38 GeV}")

# Add legend
if opt.placeLegend == "bottom_right": leg = ROOT.TLegend(0.55,0.16,0.8,0.36)
else: leg = ROOT.TLegend(0.6,0.67,0.8,0.87)
leg.SetBorderSize(0)
leg.SetFillColor(0)
#leg.SetFillStyle(0)
if opt.doBestFit: leg.AddEntry(gBF,  "Best fit", "P" )
leg.AddEntry(c68, "68% CL" , "L" )
leg.AddEntry(c95, "95% CL" , "L" )
if opt.doSM: leg.AddEntry(gSM,  "SM"     , "P" )
leg.Draw()

canv.Update()
if not os.path.isdir("./FinalPlots"): os.system("mkdir FinalPlots")
canv.SaveAs("./FinalPlots/scan2D_%s_vs_%s%s.png"%(x,y,opt.ext))
canv.SaveAs("./FinalPlots/scan2D_%s_vs_%s%s.pdf"%(x,y,opt.ext))
