#!/usr/bin/env python
# code to make second-pass stxs transfer matrix plots

from os import walk
import ROOT as r
from collections import OrderedDict as od
from usefulStyle import setCanvas, drawCMS, drawEnPu, formatHisto
from shanePalette import set_color_palette

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-l', '--lumi', default=35.9, help='set lumi')
parser.add_option('-e', '--ext', default='test', help='set extension')
(opts,args) = parser.parse_args()

r.gROOT.SetBatch(True)
r.gStyle.SetNumberContours(500)
r.gStyle.SetPaintTextFormat('2.0f')

def prettyProc( proc ):
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
  return name

#setup files 
ext          = opts.ext
lumi = float(opts.lumi)
print 'ext = %s'%ext
baseFilePath  = '/vols/cms/es811/FinalFits/ws_%s/'%ext
fileNames     = []
for root,dirs,files in walk(baseFilePath):
  for fileName in files: 
    if not fileName.startswith('output_'): continue
    if not fileName.endswith('.root'):     continue
    fileNames.append(fileName)
fullFileNames = '' 
for fileName in fileNames: fullFileNames += baseFilePath+fileName+','
fullFileNames = fullFileNames[:-1]
fullFileNames = fullFileNames.split(',')

#define processes and categories
procs         = []
for fileName in fileNames: 
  if 'M125' not in fileName: continue
  procs.append( fileName.split('pythia8_')[1].split('.root')[0] )

procsOfInterest  = ['GG2H_0J', 'GG2H_1J_PTH_0_60', 'GG2H_1J_PTH_60_120', 'GG2H_1J_PTH_120_200', 'GG2H_1J_PTH_GT200', 
                    'GG2H_GE2J_PTH_0_60', 'GG2H_GE2J_PTH_60_120', 'GG2H_GE2J_PTH_120_200', 'GG2H_GE2J_PTH_GT200', 'GG2H_VBFTOPO_JET3VETO', 'GG2H_VBFTOPO_JET3',
                    'VBF_VBFTOPO_JET3VETO', 'VBF_VBFTOPO_JET3', 'VBF_REST', 'VBF_PTJET1_GT200', 'VBF_VH2JET']

cats  = 'RECO_0J_Tag0,RECO_0J_Tag1,RECO_0J_Tag2,'
cats += 'RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_GT200,'
cats += 'RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_GT200_Tag0,RECO_GE2J_PTH_GT200_Tag1,'
cats += 'RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,RECO_VBFTOPO_REST,RECO_VBFTOPO_BSM'
cats = cats.split(',')

print procsOfInterest
print cats

nameMap  = {}
nameMap['GG2H']    = 'ggh'
nameMap['VBF']     = 'vbf'
nameMap['WH2HQQ']  = 'wh'
nameMap['ZH2HQQ']  = 'zh'
nameMap['QQ2HLL']  = 'zh'
nameMap['QQ2HLNU'] = 'wh'

sumwProcCatMap = {}
sumwProcMap = {}
for proc in procsOfInterest:
  sumwProcMap[proc] = 0.
  for cat in cats:
    sumwProcCatMap[(proc,cat)] = 0.
sumwCatMap = {}
for cat in cats:
  sumwCatMap[cat] = 0.

def main():
  for fileName in fullFileNames:
    if 'M125' not in fileName: continue
    theProc = fileName.split('pythia8_')[1].split('.root')[0]
    theProc0 = theProc.split('_')[0]
    if theProc not in procsOfInterest: continue
    print 'processing %s'%theProc
    theFile = r.TFile(fileName, 'READ')
    theWS = theFile.Get('tagsDumper/cms_hgg_13TeV')
    for cat in cats:
      dataName = '%s_125_13TeV_%s'%(nameMap[theProc0], cat)
      sumEntries = theWS.data(dataName).sumEntries()
      if sumEntries < 0.: sumEntries = 0.
      sumwProcCatMap[ (theProc,cat) ] += sumEntries
      sumwProcMap[ theProc ] += sumEntries
      sumwCatMap[ cat ] += sumEntries

  print 'got all values'
  nBinsX = len(procsOfInterest)
  nBinsY = len(cats)
  procHist = r.TH2F('procHist','procHist', nBinsX, -0.5, nBinsX-0.5, nBinsY, -0.5, nBinsY-0.5)
  procHist.SetTitle('')
  catHist  = r.TH2F('catHist','catHist', nBinsX, -0.5, nBinsX-0.5, nBinsY, -0.5, nBinsY-0.5)
  catHist.SetTitle('')
  for iProc,proc in enumerate(procsOfInterest):
    #print 'iProc,proc',iProc,proc
    for iCat,cat in enumerate(cats):
      procWeight = 100. * sumwProcCatMap[(proc,cat)] / sumwProcMap[proc]
      if procWeight < 0.5: procWeight=-1
      catWeight  = 100. * sumwProcCatMap[(proc,cat)] / sumwCatMap[cat]
      if catWeight < 0.5: catWeight=-1

      catLabel = cat.split('ECO_')[1]
      catLabel = catLabel.replace('PTH_0_60','low')
      catLabel = catLabel.replace('PTH_60_120','med')
      catLabel = catLabel.replace('PTH_120_200','high')
      catLabel = catLabel.replace('PTH_GT200','BSM')
      catLabel = catLabel.replace('GE2J','2J')
      catLabel = catLabel.replace('PTJET1_GT200','BSM')
      catLabel = catLabel.replace('VBFTOPO','VBF')
      catLabel = catLabel.replace('JET3VETO','2J-like')
      catLabel = catLabel.replace('JET3','3J-like')
      catLabel = catLabel.replace('VH2JET','VH-like')
      catLabel = catLabel.replace('REST','rest')
      catLabel = catLabel.replace('_',' ')

      procHist.Fill( iProc, iCat, procWeight )
      procHist.GetXaxis().SetBinLabel( iProc+1, prettyProc(proc) )
      procHist.GetYaxis().SetBinLabel( iCat+1, catLabel )

      catHist.Fill( iProc, iCat, catWeight )
      catHist.GetXaxis().SetBinLabel( iProc+1, prettyProc(proc) )
      catHist.GetYaxis().SetBinLabel( iCat+1, catLabel )
  
  #canv = r.TCanvas('canv','canv')
  set_color_palette('ed_noice')
  canv = setCanvas()
  formatHisto(procHist)
  procHist.SetStats(0)
  procHist.GetXaxis().SetTitle('STXS process')
  procHist.GetXaxis().SetTitleOffset(3)
  procHist.GetXaxis().SetTickLength(0.)
  procHist.GetXaxis().LabelsOption('v')
  procHist.GetYaxis().SetTitle('Event category')
  procHist.GetYaxis().SetTitleOffset(2.7)
  procHist.GetYaxis().SetTickLength(0.)
  procHist.GetZaxis().SetTitle('Signal category destination (%)')
  procHist.SetMinimum(-0.00001)
  procHist.SetMaximum(100.)
  procHist.Draw('colz,text')
  lines = []
  for iProc,proc in enumerate(procsOfInterest):
    lines.append(r.TLine(iProc+0.5, -0.5, iProc+0.5, len(cats)-0.5))
    lines[-1].SetLineColorAlpha(r.kGray, 0.5)
    lines[-1].SetLineWidth(1)
  lines.append(r.TLine(-0.5, 16.5, len(procsOfInterest)-0.5, 16.5)) #horiontal ggH VBF divider
  lines[-1].SetLineColorAlpha(r.kBlack, 0.5)
  lines[-1].SetLineWidth(1)
  lines.append(r.TLine(10.5, -0.5, 10.5, len(cats)-0.5)) #vertical ggH VBF divider
  lines[-1].SetLineColorAlpha(r.kBlack, 0.5)
  lines[-1].SetLineWidth(1)
  for line in lines: line.Draw()
  drawCMS(True)
  drawEnPu(lumi='%.1f fb^{-1}'%lumi)
  canv.Print('procHist_%s.pdf'%ext)
  canv.Print('procHist_%s.png'%ext)
  formatHisto(catHist)
  catHist.SetStats(0)
  catHist.GetXaxis().SetTitle('STXS process')
  catHist.GetXaxis().SetTitleOffset(3)
  catHist.GetXaxis().SetTickLength(0.)
  catHist.GetXaxis().LabelsOption('v')
  catHist.GetYaxis().SetTitle('Event category')
  catHist.GetYaxis().SetTitleOffset(2.7)
  catHist.GetYaxis().SetTickLength(0.)
  catHist.GetZaxis().SetTitle('Category signal composition (%)')
  catHist.SetMinimum(-0.00001)
  catHist.SetMaximum(100.)
  catHist.Draw('colz,text')
  lines = []
  for iCat,cat in enumerate(cats):
    if cat.count('Tag1') or cat.count('RECO_1J_PTH_GT200') or cat.count('RECO_VBFTOPO_REST'):
      lines.append(r.TLine(-0.5, iCat+0.5, len(procsOfInterest)-0.5, iCat+0.5))
      lines[-1].SetLineColorAlpha(r.kGray, 0.5)
      lines[-1].SetLineWidth(1)
    else:
      lines.append(r.TLine(-0.5, iCat+0.5, len(procsOfInterest)-0.5, iCat+0.5))
      lines[-1].SetLineColorAlpha(r.kGray, 0.25)
      lines[-1].SetLineWidth(1)
  lines.append(r.TLine(-0.5, 17.5, len(procsOfInterest)-0.5, 17.5)) #horiontal ggH VBF divider
  lines[-1].SetLineColorAlpha(r.kBlack, 0.5)
  lines[-1].SetLineWidth(1)
  lines.append(r.TLine(10.5, -0.5, 10.5, len(cats)-0.5)) #vertical ggH VBF divider
  lines[-1].SetLineColorAlpha(r.kBlack, 0.5)
  lines[-1].SetLineWidth(1)
  for line in lines: line.Draw()
  drawCMS(True)
  drawEnPu(lumi='%.1f fb^{-1}'%lumi)
  canv.Print('catHist_%s.pdf'%ext)
  canv.Print('catHist_%s.png'%ext)
  #save hists
  outFile = r.TFile('stxsStage1Hists_%s.root'%ext,'RECREATE')
  procHist.Write()
  catHist.Write()
  outFile.Close()


if __name__ == '__main__':
  main()
