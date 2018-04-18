#!/usr/bin/env python
# code to make second-pass stxs transfer matrix plots

from os import walk
import ROOT as r
from collections import OrderedDict as od

#from optparse import OptionParser
#parser = OptionParser()
#parser.add_option('-k', '--key', default='GluGluHToGG', help='choose the sample to run on')
#parser.add_option('-d', '--doLoose', default=False, action='store_true', help='use loose photons (default false, ie use only tight photons)')
#(opts,args) = parser.parse_args()

r.gROOT.SetBatch(True)

#setup files 
#ext          = 'fullStage1Test'
ext          = 'fullerStage1Test'
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
#procsOfInterest = procs
procsOfInterest = ['GG2H_0J','GG2H_1J_PTH_0_60','GG2H_1J_PTH_60_120','GG2H_1J_PTH_120_200','GG2H_1J_PTH_GT200','GG2H_GE2J_PTH_0_60','GG2H_GE2J_PTH_60_120','GG2H_GE2J_PTH_120_200','GG2H_GE2J_PTH_GT200']
#cats          = 'NOTAG,RECO_0J,RECO_1J_PTH_0_60,RECO_1J_PTH_60_120,RECO_1J_PTH_120_200,RECO_1J_PTH_GT200,RECO_GE2J_PTH_0_60,RECO_GE2J_PTH_60_120,RECO_GE2J_PTH_120_200,RECO_GE2J_PTH_GT200,RECO_VBFTOPO_JET3VETO,RECO_VBFTOPO_JET3,RECO_VH2JET,RECO_0LEP_PTV_0_150,RECO_0LEP_PTV_150_250_0J,RECO_0LEP_PTV_150_250_GE1J,RECO_0LEP_PTV_GT250,RECO_1LEP_PTV_0_150,RECO_1LEP_PTV_150_250_0J,RECO_1LEP_PTV_150_250_GE1J,RECO_1LEP_PTV_GT250,RECO_2LEP_PTV_0_150,RECO_2LEP_PTV_150_250_0J,RECO_2LEP_PTV_150_250_GE1J,RECO_2LEP_PTV_GT250,RECO_TTH_LEP,RECO_TTH_HAD'
cats          = 'RECO_0J,RECO_1J_PTH_0_60,RECO_1J_PTH_60_120,RECO_1J_PTH_120_200,RECO_1J_PTH_GT200,RECO_GE2J_PTH_0_60,RECO_GE2J_PTH_60_120,RECO_GE2J_PTH_120_200,RECO_GE2J_PTH_GT200'
cats = cats.split(',')
print procs 
print cats

nameMap  = {}
nameMap['GG2H']    = 'ggh'
nameMap['VBF']     = 'vbf'
nameMap['WH2HQQ']  = 'wh'
nameMap['ZH2HQQ']  = 'zh'
nameMap['QQ2HLL']  = 'zh'
nameMap['QQ2HLNU'] = 'wh'

procLabelMap = {'GG2H_0J':'0j','GG2H_1J_PTH_0_60':'1j low','GG2H_1J_PTH_60_120':'1j med','GG2H_1J_PTH_120_200':'1j high','GG2H_1J_PTH_GT200':'1j BSM','GG2H_GE2J_PTH_0_60':'2j low','GG2H_GE2J_PTH_60_120':'2j med','GG2H_GE2J_PTH_120_200':'2j high','GG2H_GE2J_PTH_GT200':'2j BSM'}

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
  nBins = len(procsOfInterest)
  procHist = r.TH2F('procHist','procHist', nBins, -0.5, nBins-0.5, nBins, -0.5, nBins-0.5)
  procHist.SetTitle('')
  catHist  = r.TH2F('catHist','catHist', nBins, -0.5, nBins-0.5, nBins, -0.5, nBins-0.5)
  catHist.SetTitle('')
  for iProc,proc in enumerate(procsOfInterest):
    print 'pProc,proc',iProc,proc
    for iCat,cat in enumerate(cats):
      procWeight = 100. * sumwProcCatMap[(proc,cat)] / sumwProcMap[proc]
      catWeight  = 100. * sumwProcCatMap[(proc,cat)] / sumwCatMap[cat]

      procHist.Fill( iProc, iCat, procWeight )
      procHist.GetXaxis().SetBinLabel( iProc+1, procLabelMap[proc] )
      procHist.GetYaxis().SetBinLabel( iProc+1, procLabelMap[proc] )

      catHist.Fill( iProc, iCat, catWeight )
      catHist.GetXaxis().SetBinLabel( iProc+1, procLabelMap[proc] )
      catHist.GetYaxis().SetBinLabel( iProc+1, procLabelMap[proc] )
  
  canv = r.TCanvas('canv','canv')
  r.gStyle.SetPaintTextFormat('2.0f')
  procHist.SetStats(0)
  procHist.GetXaxis().SetTitle('Process')
  procHist.GetXaxis().SetTickLength(0.)
  procHist.GetYaxis().SetTitle('Category')
  procHist.GetYaxis().SetTitleOffset(1.5)
  procHist.GetYaxis().SetTickLength(0.)
  procHist.SetMinimum(-0.00001)
  procHist.SetMaximum(100.)
  procHist.Draw('colz,text')
  canv.Print('procHist.pdf')
  canv.Print('procHist.png')
  catHist.SetStats(0)
  catHist.GetXaxis().SetTitle('Process')
  catHist.GetXaxis().SetTickLength(0.)
  catHist.GetYaxis().SetTitle('Category')
  catHist.GetYaxis().SetTitleOffset(1.5)
  catHist.GetYaxis().SetTickLength(0.)
  catHist.SetMinimum(-0.00001)
  catHist.SetMaximum(100.)
  catHist.Draw('colz,text')
  canv.Print('catHist.pdf')
  canv.Print('catHist.png')
  #save hists
  outFile = r.TFile('stxsStage1Hists.root','RECREATE')
  procHist.Write()
  catHist.Write()
  outFile.Close()


if __name__ == '__main__':
  main()
