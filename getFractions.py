#!/usr/bin/env python
# code to make first-pass stxs transfer matrix plots

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
ext          = 'fullStage1Test'
#ext          = 'reCategorised'
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
procs      = od()
procsNoTag = od()
for fileName in fileNames: 
  if 'M125' not in fileName: continue
  procs[ fileName.split('pythia8_')[1].split('.root')[0] ] = 0.
  procsNoTag[ fileName.split('pythia8_')[1].split('.root')[0] ] = 0.
cats          = 'RECO_0J,RECO_1J_PTH_0_60,RECO_1J_PTH_60_120,RECO_1J_PTH_120_200,RECO_1J_PTH_GT200,RECO_GE2J_PTH_0_60,RECO_GE2J_PTH_60_120,RECO_GE2J_PTH_120_200,RECO_GE2J_PTH_GT200,RECO_VBFTOPO_JET3VETO,RECO_VBFTOPO_JET3,RECO_VH2JET,RECO_0LEP_PTV_0_150,RECO_0LEP_PTV_150_250_0J,RECO_0LEP_PTV_150_250_GE1J,RECO_0LEP_PTV_GT250,RECO_1LEP_PTV_0_150,RECO_1LEP_PTV_150_250_0J,RECO_1LEP_PTV_150_250_GE1J,RECO_1LEP_PTV_GT250,RECO_2LEP_PTV_0_150,RECO_2LEP_PTV_150_250_0J,RECO_2LEP_PTV_150_250_GE1J,RECO_2LEP_PTV_GT250,RECO_TTH_LEP,RECO_TTH_HAD'
#cats  = 'RECO_0J_Tag0,RECO_0J_Tag1,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_GT200,'
#cats += 'RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_GT200_Tag0,RECO_GE2J_PTH_GT200_Tag1,RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,'
#cats += 'RECO_WHLEP,RECO_ZHLEP,RECO_VHLEPLOOSE,RECO_VHMET,RECO_VHHAD,'
#cats += 'RECO_TTH_LEP,RECO_TTH_HAD'
cats = cats.split(',')
stage0procs = {}
stage0procs['GG2H']    = 0.
stage0procs['VBF']     = 0.
stage0procs['WH2HQQ']  = 0.
stage0procs['ZH2HQQ']  = 0.
stage0procs['QQ2HLL']  = 0.
stage0procs['QQ2HLNU'] = 0.
stage0procs['TTH'] = 0.

stage0noTag = {}
stage0noTag['GG2H']    = 0.
stage0noTag['VBF']     = 0.
stage0noTag['WH2HQQ']  = 0.
stage0noTag['ZH2HQQ']  = 0.
stage0noTag['QQ2HLL']  = 0.
stage0noTag['QQ2HLNU'] = 0.
stage0noTag['TTH'] = 0.
print procs 
print cats

nameMap  = {}
nameMap['GG2H']    = 'ggh'
nameMap['VBF']     = 'vbf'
nameMap['WH2HQQ']  = 'wh'
nameMap['ZH2HQQ']  = 'zh'
nameMap['QQ2HLL']  = 'zh'
nameMap['QQ2HLNU'] = 'wh'
nameMap['TTH'] = 'tth'

def main():
  #checkZeros()
  #exit(0)
  totEffAccNumer = 0.
  totEffAccDenom = 0.
  for fileName in fullFileNames:
    if 'M125' not in fileName: continue
    theProc = fileName.split('pythia8_')[1].split('.root')[0]
    theProc0 = theProc.split('_')[0]
    print 'processing %s'%theProc
    theFile = r.TFile(fileName, 'READ')
    theWS = theFile.Get('tagsDumper/cms_hgg_13TeV')
    for cat in cats:
      dataName = '%s_125_13TeV_%s'%(nameMap[theProc0], cat)
      sumEntries = theWS.data(dataName).sumEntries()
      stage0procs[theProc0] += sumEntries
      procs[theProc] += sumEntries
      totEffAccNumer += sumEntries
    dataName = '%s_125_13TeV_NOTAG'%(nameMap[theProc0])
    sumEntries = theWS.data(dataName).sumEntries()
    stage0noTag[theProc0] += sumEntries
    procsNoTag[theProc] += sumEntries
    totEffAccDenom += sumEntries

  print '\n\n\nStage 1 fractions:'
  for proc,val in procs.iteritems():
    procTot = stage0procs[ proc.split('_')[0] ]
    theFrac = val / procTot
    effAcc  = val / (val + procsNoTag[proc]) 
    print 'total     for process %s is %1.4f'%(proc,35.9*val)
    print 'fraction  for process %s is %1.4f'%(proc,theFrac)
    print 'eff x acc for process %s is %1.4f'%(proc,effAcc)
    print
  print '\n'
  totEffAcc = totEffAccNumer / (totEffAccNumer + totEffAccDenom)
  print 'total eff x acc is %1.4f'%(totEffAcc)

def checkZeros():
  print 'About to check for low sumEntries'
  #masses = [120,123,124,125,126,127,130]
  masses = [120,125,130]
  for mass in masses:
    mass = str(mass)
    print 'processing mass %s'%mass
    for fileName in fullFileNames:
      if 'M%s'%mass not in fileName: continue
      theProc = fileName.split('pythia8_')[1].split('.root')[0]
      theProc0 = theProc.split('_')[0]
      print 'processing %s'%theProc
      theFile = r.TFile(fileName, 'READ')
      theWS = theFile.Get('tagsDumper/cms_hgg_13TeV')
      for cat in cats:
        dataName = '%s_%s_13TeV_%s'%(nameMap[theProc0], mass, cat)
        sumEntries = theWS.data(dataName).sumEntries()
        if sumEntries < 0.1:
          print 'WARNING: sumEntries is %1.3f for %s, %s at %s GeV'%(sumEntries, theProc, cat, mass)

if __name__ == '__main__':
  main()
