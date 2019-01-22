from shanePalette import set_color_palette
from usefulStyle import drawCMS, drawEnPu, setCanvas, formatHisto
from collections import OrderedDict as od
import ROOT as r

r.gROOT.SetBatch(True)
r.gStyle.SetNumberContours(500)

lumi = 35.9

exts = ['Stage0','Stage1','Stage1Minimal']

def prettyProc( proc ):
  if proc.startswith('r_'): proc = proc.split('r_')[1]
  if proc.startswith('GG2H_'):
    name = 'ggH '
    proc = proc.split('GG2H_')[1]
    proc = proc.replace('VBFTOPO_JET3VETO','VBF-like 2J')
    proc = proc.replace('VBFTOPO_JET3','VBF-like 3J')
    proc = proc.replace('PTH_0_60','low')
    proc = proc.replace('PTH_0_60','low')
    proc = proc.replace('PTH_60_120','med')
    proc = proc.replace('PTH_120_200','high')
    proc = proc.replace('PTH_GT200','BSM')
    proc = proc.replace('GE2J','2J')
    proc = proc.replace('_',' ')
    name = name + proc
  elif proc.startswith('VBF_'):
    name = 'VBF '
    proc = proc.split('VBF_')[1]
    proc = proc.replace('PTJET1_GT200','BSM')
    proc = proc.replace('VBFTOPO','')
    proc = proc.replace('JET3VETO','2J-like')
    proc = proc.replace('JET3','3J-like')
    proc = proc.replace('VH2JET','VH-like')
    proc = proc.replace('REST','rest')
    proc = proc.replace('_',' ')
    name = name + proc
  else:
    name = ''
    proc = proc.replace('VBFTOPO_JET3VETO','VBF-like 2J')
    proc = proc.replace('VBFTOPO_JET3','VBF-like 3J')
    proc = proc.replace('VBFTOPO','VBF-like')
    proc = proc.replace('PTJET1_GT200','BSM')
    proc = proc.replace('JET3VETO','2J-like')
    proc = proc.replace('JET3','3J-like')
    proc = proc.replace('VH2JET','VH-like')
    proc = proc.replace('REST','rest')
    proc = proc.replace('PTH_0_60','low')
    proc = proc.replace('PTH_0_60','low')
    proc = proc.replace('PTH_60_120','med')
    proc = proc.replace('PTH_120_200','high')
    proc = proc.replace('PTH_GT200','BSM')
    proc = proc.replace('GE2J','2J')
    proc = proc.replace('_',' ')
    name = name + proc
  return name

for ext in exts:
  fileName = '%s/robustHesse_robustHesse.root'%ext
  inFile = r.TFile(fileName,'READ')
  theMatrix = inFile.Get('h_correlation')
  theList   = inFile.Get('floatParsFinal')

  pars = od()
  for iPar,par in enumerate(theList):
    if iPar==len(theList)-1: break
    if not par.GetName().startswith('r_'): continue
    pars[par.GetName()] = iPar
  nPars = len(pars.keys())
  print 'Procesing the following %g parameters:'%nPars
  for par in pars.keys(): print par
  revPars = {i:name for name,i in pars.iteritems()}

  theHist = r.TH2F('corr_%s'%ext, '', nPars, -0.5, nPars-0.5, nPars, -0.5, nPars-0.5)

  for iBin,iPar in enumerate(pars.values()):
    for jBin,jPar in enumerate(pars.values()):
      proc = theMatrix.GetXaxis().GetBinLabel(iPar+1)
      #print 'Got proc %s, expecting proc %s'%(proc, revPars[iPar])
      theVal = theMatrix.GetBinContent(iPar+1,jPar+1)
      #print 'Value for correlation between %s and %s is %.3f'%(revPars[iPar],revPars[jPar],theVal)
      theHist.GetXaxis().SetBinLabel(iBin+1, prettyProc(revPars[iPar]))
      theHist.GetYaxis().SetBinLabel(jBin+1, prettyProc(revPars[jPar]))
      theHist.Fill(iBin, jBin, theVal)

  set_color_palette('frenchFlag')
  r.gStyle.SetNumberContours(500)
  r.gStyle.SetPaintTextFormat('1.2f')

  #canv = r.TCanvas('canv','canv')
  canv = setCanvas()
  formatHisto(theHist)
  theHist.GetXaxis().SetTickLength(0.)
  theHist.GetXaxis().SetLabelSize(0.05)
  theHist.GetYaxis().SetTickLength(0.)
  theHist.GetYaxis().SetLabelSize(0.05)
  theHist.GetZaxis().SetRangeUser(-1.,1.)
  theHist.GetZaxis().SetTickLength(0.)

  theHist.Draw('colz,text')
  drawCMS(True)
  drawEnPu(lumi='%2.1f fb^{-1}'%lumi)
  canv.Print('Plots/corrMatrixFormal_%s.png'%ext)
  canv.Print('Plots/corrMatrixFormal_%s.pdf'%ext)
