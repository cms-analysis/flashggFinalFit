from optparse import OptionParser
from shanePalette import set_color_palette
from usefulStyle import drawCMS, drawEnPu, setCanvasCorr, formatHisto, setCanvas
from collections import OrderedDict as od
import ROOT
import json
import os
import re

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='', help='Type of fit')
  parser.add_option('--ext', dest='ext', default='', help='If running with extension in datacard')
  parser.add_option('--translate', dest='translate', default=None, help='Load translations for pois')
  parser.add_option('--doCov', dest='doCov', default=False, action="store_true", help='Do covariance matrix')
  parser.add_option('--input', dest='input', default='./robustHessefirstStep.root', help='Input file for plotting.')
  parser.add_option('--output', dest='output', default='', help='Output folder for plotting.')
  parser.add_option('--dropTHQ', dest='dropTHQ', default=False, action="store_true", help='Drop r_tHq from the poi list')
  parser.add_option('--doObserved', dest='doObserved', default=False, action="store_true", help='Do observed correlation')
  return parser.parse_args()
(opt,args) = get_options() 

def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
      
def Translate(name, ndict):
    return ndict[name] if name in ndict else name

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetNumberContours(500)
lumi = 34.7

if opt.doObserved: obs_ext = "_obs"
else: obs_ext = ''

modes = od()

# Read json file and extract pois
with open( opt.inputJson ) as jsonfile: inputs = json.load(jsonfile)[opt.mode]
pois = inputs['pois'].split(",") 
if(opt.dropTHQ)&("r_tHq" in pois): pois.remove("r_tHq")
fit = inputs['fits'].split("+")[0]
name = "%s_%s"%(fit.split(":")[0],fit.split(":")[1])
modes[opt.mode] = pois
# Load translations
translate = {} if opt.translate is None else LoadTranslations(opt.translate)

for mode,pois in modes.items():
  fileName = opt.input
  # fileName = '%s/src/flashggFinalFit/Combine/runFits%s_%s/robustHesse_%s%s.root'%(os.environ['CMSSW_BASE'],opt.ext,opt.mode,name,obs_ext)
  inFile = ROOT.TFile(fileName,'READ')
  if opt.doCov: 
    theMatrix = inFile.Get('h_covariance')
  else:
    theMatrix = inFile.Get('h_correlation')
  theList   = inFile.Get('floatParsFinal')

  pars = od()
  for iPar,par in enumerate(theList):
    if iPar==len(theList)-1: break
    if not par.GetName().startswith('r_'): continue
    pars[par.GetName()] = iPar
  nPars = len(list(pars.keys()))
  print('Procesing the following %g parameters:'%nPars)
  for par in list(pars.keys()): print(par)
  revPars = {i:name for name,i in pars.items()}

  theHist = ROOT.TH2F('corr_%s'%mode, '', nPars, -0.5, nPars-0.5, nPars, -0.5, nPars-0.5)
  theMap = {}
  theMapToJson = {}

  for iBin,iPar in enumerate(pars.values()):
    for jBin,jPar in enumerate(pars.values()):
      proc = theMatrix.GetXaxis().GetBinLabel(iPar+1)
      #print('Got proc %s, expecting proc %s'%(proc, revPars[iPar]))
      theVal = theMatrix.GetBinContent(iPar+1,jPar+1)
      #print('Value for correlation between %s and %s is %.3f'%(revPars[iPar],revPars[jPar],theVal))
      theMap[(revPars[iPar],revPars[jPar])] = theVal
      theMapToJson[ "%s__%s"%(revPars[iPar],revPars[jPar]) ] = theVal

  # Output json file storing correlaiton and parameters
  #with open("correlations_expected_%s.json"%mode,"w") as jf: json.dump(theMapToJson,jf)
  
  pois_reverse = list(pois)
  pois_reverse.reverse()
  for iBin,iPar in enumerate(pois):
    for jBin,jPar in enumerate(pois_reverse):
      if opt.translate is not None:
        theHist.GetXaxis().SetBinLabel(iBin+1, translate[iPar])
        theHist.GetYaxis().SetBinLabel(jBin+1, translate[jPar])
      else:
        theHist.GetXaxis().SetBinLabel(iBin+1, iPar)
        theHist.GetYaxis().SetBinLabel(jBin+1, jPar)

      #print('Filling correlation for %s and %s of %.3f'%(iPar, jPar, theMap[(iPar,jPar)]))
      if iBin <= (theHist.GetNbinsX()-1-jBin): theHist.Fill(iBin, jBin, theMap[(iPar,jPar)])

  print('Final correlation map used is:')
  print(theMap)

  # set_color_palette('frenchFlag')
  set_color_palette('gradient_8289')
  ROOT.gStyle.SetNumberContours(500)
  ROOT.gStyle.SetPaintTextFormat('1.2f')
  ROOT.gStyle.SetTextFont(42)

  if mode.count('stage1p2'): canv = setCanvasCorr(stage='1p2')
  elif mode.count('mu_reco'): canv = setCanvasCorr(stage='1p2')
  else:
    if opt.doCov:
      canv = setCanvas()
    else:
      canv = setCanvasCorr()
  formatHisto(theHist)
  theHist.GetXaxis().SetTickLength(0.)
  theHist.GetXaxis().SetLabelSize(0.06)
  theHist.GetXaxis().SetLabelFont(42)
  theHist.GetYaxis().SetTickLength(0.)
  theHist.GetYaxis().SetLabelSize(0.06)
  theHist.GetYaxis().SetLabelOffset(0.003)
  theHist.GetYaxis().SetLabelFont(42)
  if opt.doCov:
    theHist.GetZaxis().SetRangeUser(-0.5,0.5)
  else:
    theHist.GetZaxis().SetRangeUser(-1., 1.)
  theHist.GetZaxis().SetTickLength(0.)
  theHist.GetZaxis().SetLabelSize(0.03)
  if mode.count('stage1p2'): 
    theHist.GetXaxis().SetLabelOffset(0.003)
    theHist.GetXaxis().LabelsOption("v")
    if ( mode.count('extended') ):
      theHist.GetXaxis().SetLabelSize(0.025)
      theHist.GetYaxis().SetLabelSize(0.025)
      theHist.SetMarkerSize(0.55)
    elif( mode.count('minimal') ):
      theHist.GetXaxis().SetLabelSize(0.02)
      theHist.GetYaxis().SetLabelSize(0.02)
      theHist.SetMarkerSize(0.6)
    else:
      theHist.GetXaxis().SetLabelSize(0.03)
      theHist.GetYaxis().SetLabelSize(0.03)
      theHist.SetMarkerSize(0.8)
  elif mode.count('stage0'):
    theHist.GetXaxis().LabelsOption("h")
    theHist.GetYaxis().SetLabelOffset(0.007)
    theHist.SetMarkerSize(1.5)
    theHist.GetXaxis().SetLabelSize(0.05)
    theHist.GetYaxis().SetLabelSize(0.05)
  elif mode.count('mu_reco'): 
    theHist.GetXaxis().SetLabelOffset(0.003)
    theHist.GetXaxis().LabelsOption("v")
    theHist.GetXaxis().SetLabelSize(0.025)
    theHist.GetYaxis().SetLabelSize(0.025)
    theHist.SetMarkerSize(0.55)
  else:
    theHist.GetXaxis().SetLabelOffset(0.003)
    theHist.GetXaxis().LabelsOption("v")
    if opt.doCov:
      if mode.count("PTH"):
        label_size = 0.035
        theHist.GetXaxis().SetLabelSize(label_size)
        theHist.GetYaxis().SetLabelSize(label_size)
        theHist.SetMarkerSize(2)
      else:
        label_size = 0.04
        theHist.GetXaxis().SetLabelSize(label_size)
        theHist.GetYaxis().SetLabelSize(label_size)
        theHist.SetMarkerSize(2)
    else:
      if mode.count("PTH"):
        label_size = 0.035
      elif mode.count("rapidity"):
        label_size = 0.04
      elif mode.count("Njets2p5"):
        label_size = 0.045
      else:
        label_size = 0.03
      theHist.GetXaxis().SetLabelSize(label_size)
      theHist.GetYaxis().SetLabelSize(label_size)
      theHist.SetMarkerSize(1.5)
  # else:
  #   theHist.GetYaxis().SetLabelOffset(0.007)  
  #   theHist.SetMarkerSize(1.5)
  theHist.Draw('colz,text')
  latex = ROOT.TLatex()
  latex.SetNDC()
  latex.SetTextFont(42)
  latex.SetTextAlign(32)
  latex.SetTextSize(0.045)
  if opt.doObserved:
    latex.DrawLatex(1.00-canv.GetRightMargin()-0.02,1.00-canv.GetTopMargin()-0.06,'#bf{CMS} #it{Preliminary}')
  else:
    latex.DrawLatex(1.00-canv.GetRightMargin()-0.02,1.00-canv.GetTopMargin()-0.06,'#bf{CMS} #it{Simulation Preliminary}')
  latex.SetTextSize(0.04)
  latex.DrawLatex(1.00-canv.GetRightMargin()-0.02,1.00-canv.GetTopMargin()-0.12,'%0.2f fb^{-1} (13.6 TeV)'%lumi)
  latex.SetTextSize(0.025)
  latex.DrawLatex(1.00-canv.GetRightMargin()-0.02,1.00-canv.GetTopMargin()-0.18,'H #rightarrow #gamma#gamma, m_{H} = 125.38 GeV')
  for binx in range(1, theHist.GetNbinsX() + 1):
    for biny in range(1, theHist.GetNbinsY() + 1):
        if (theHist.GetBinContent(binx, biny)) > 0.8:
            label = "{:.2f}".format(theHist.GetBinContent(binx, biny))
            latex = ROOT.TLatex()
            latex.SetTextAlign(22)  # Center align text
            latex.SetTextSize(0.03)  # Set text size as needed
            latex.SetTextColor(ROOT.kWhite)  # Set text color to white
            latex.DrawLatex(theHist.GetXaxis().GetBinCenter(binx), theHist.GetYaxis().GetBinCenter(biny), label)
  #canv.Print("/eos/home-j/jlangfor/www/CMS/hgg/stxs_runII/May20/pass0/test/test_%s.png"%opt.mode)
  #canv.Print("/eos/home-j/jlangfor/www/CMS/hgg/stxs_runII/May20/pass0/test/test_%s.pdf"%opt.mode)
  #canv.Print('%s/src/flashggFinalFit/Combine/runFits%s_%s/Plots/corrMatrix_%s_%s%s%s.png'%(os.environ['CMSSW_BASE'],opt.ext,mode,mode,name.split("_")[-1],obs_ext,opt.ext))
  #canv.Print('%s/src/flashggFinalFit/Combine/runFits%s_%s/Plots/corrMatrix_%s_%s%s%s.pdf'%(os.environ['CMSSW_BASE'],opt.ext,mode,mode,name.split("_")[-1],obs_ext,opt.ext))
  output_dir = opt.output
  if opt.doCov:
    output_path_png = os.path.join(opt.output, "covMatrix_%s_%s%s%s.png"%(mode,name.split("_")[-1],obs_ext,opt.ext))
    output_path_pdf = os.path.join(opt.output, "covMatrix_%s_%s%s%s.pdf"%(mode,name.split("_")[-1],obs_ext,opt.ext))
    canv.Print(output_path_png)
    canv.Print(output_path_pdf)
  else:
    output_path_png = os.path.join(opt.output, "corrMatrix_%s_%s%s%s.png"%(mode,name.split("_")[-1],obs_ext,opt.ext))
    output_path_pdf = os.path.join(opt.output, "corrMatrix_%s_%s%s%s.pdf"%(mode,name.split("_")[-1],obs_ext,opt.ext))
    canv.Print(output_path_png)
    canv.Print(output_path_pdf)
   
