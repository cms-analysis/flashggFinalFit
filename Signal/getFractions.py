#!/usr/bin/env python
# code to make first-pass stxs transfer matrix plots

from os import listdir
import ROOT as r
r.gROOT.SetBatch(True)
from collections import OrderedDict as od
import re, sys

catsSplittingScheme = {
  'tagsetone':['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2'],
  'tagsettwo':['RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_450_650_Tag1', 'RECO_PTH_GT650_Tag0', 'RECO_PTH_GT650_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1'],
  'tagsetthree':['RECO_TTH_HAD_LOW_Tag0', 'RECO_TTH_HAD_LOW_Tag1', 'RECO_TTH_HAD_LOW_Tag2', 'RECO_TTH_HAD_LOW_Tag3', 'RECO_TTH_HAD_HIGH_Tag0', 'RECO_TTH_HAD_HIGH_Tag1', 'RECO_TTH_HAD_HIGH_Tag2', 'RECO_TTH_HAD_HIGH_Tag3', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'RECO_TTH_LEP_LOW_Tag0', 'RECO_TTH_LEP_LOW_Tag1', 'RECO_TTH_LEP_LOW_Tag2', 'RECO_TTH_LEP_LOW_Tag3', 'RECO_TTH_LEP_HIGH_Tag0', 'RECO_TTH_LEP_HIGH_Tag1', 'RECO_TTH_LEP_HIGH_Tag2', 'RECO_TTH_LEP_HIGH_Tag3', 'RECO_THQ_LEP']
  }

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-e', '--ext', default='test', help='name of analysis')
parser.add_option('-f', '--filePath', default='test', help='directory of files')
parser.add_option('-c', '--cats', default='test', help='analysis categories')
parser.add_option('--tagSplit', dest='tagSplit', default=False, action="store_true", help="If tags are split according to above splitting scheme")
(opts,args) = parser.parse_args()

# Extract processes and nominal names from tagsetone
baseFilePath  = opts.filePath
if not baseFilePath.endswith('/'): baseFilePath += '/'
if opts.tagSplit: baseFilePath += "tagsetone/"

fileNames     = []
for fileName in listdir(baseFilePath): 
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

cats = opts.cats
cats = cats.split(',')
stage0procs = {}
stage0procs['GG2H']    = 0.
stage0procs['VBF']     = 0.
stage0procs['WH2HQQ']  = 0.
stage0procs['ZH2HQQ']  = 0.
stage0procs['QQ2HLL']  = 0.
stage0procs['QQ2HLNU'] = 0.
stage0procs['TTH'] = 0.
stage0procs['TH'] = 0.

stage0noTag = {}
stage0noTag['GG2H']    = 0.
stage0noTag['VBF']     = 0.
stage0noTag['WH2HQQ']  = 0.
stage0noTag['ZH2HQQ']  = 0.
stage0noTag['QQ2HLL']  = 0.
stage0noTag['QQ2HLNU'] = 0.
stage0noTag['TTH'] = 0.
stage0noTag['TH'] = 0.
print " --> [DEBUG] PROCS: ", procs.keys
print " --> [DEBUG] CATS: ", cats

nameMap  = {}
nameMap['GG2H']    = 'ggh'
nameMap['VBF']     = 'vbf'
nameMap['WH2HQQ']  = 'wh'
nameMap['ZH2HQQ']  = 'zh'
nameMap['QQ2HLL']  = 'zh'
nameMap['QQ2HLNU'] = 'wh'
nameMap['TTH'] = 'tth'
nameMap['TH'] = 'th'

print nameMap

granularMap = {}

def main():
  #checkZeros()
  #exit(0)
  totEffAccNumer = 0.
  totEffAccDenom = 0.
  for fileName in fullFileNames:
    if 'M125' not in fileName: continue
    theProc = fileName.split('pythia8_')[1].split('.root')[0]
    theProc0 = theProc.split('_')[0]
    print 'processing %s (%s)'%(theProc,theProc0)
    theFile = r.TFile(fileName, 'READ')
    theWS = theFile.Get('tagsDumper/cms_hgg_13TeV')
    if opts.tagSplit:
      theFile2 = r.TFile( re.sub("tagsetone","tagsettwo",fileName), 'READ')
      theWS2 = theFile2.Get('tagsDumper/cms_hgg_13TeV')
      theFile3 = r.TFile( re.sub("tagsetone","tagsetthree",fileName), 'READ')
      theWS3 = theFile3.Get('tagsDumper/cms_hgg_13TeV')
      for cat in cats:
        dataName = '%s_125_13TeV_%s'%(nameMap[theProc0], cat)
        granularKey = '%s__%s'%(theProc,cat)
        if cat in catsSplittingScheme['tagsetone']: sumEntries = theWS.data(dataName).sumEntries()
        elif cat in catsSplittingScheme['tagsettwo']: sumEntries = theWS2.data(dataName).sumEntries()
        elif cat in catsSplittingScheme['tagsetthree']: sumEntries = theWS3.data(dataName).sumEntries()
        else: 
          print " --> [ERROR] cat not defined in tag splitting scheme. Leaving"
          sys.exit(1)
        if not granularKey in granularMap: granularMap[granularKey] = sumEntries
        else: exit('DO NOT expect a given proc x cat to appear more than once!!!')
        stage0procs[theProc0] += sumEntries
        procs[theProc] += sumEntries
        totEffAccNumer += sumEntries
    else:  
      for cat in cats:
	sumEntries = theWS.data(dataName).sumEntries()
	if not granularKey in granularMap: granularMap[granularKey] = sumEntries
	else: exit('DO NOT expect a given proc x cat to appear more than once!!!')
	stage0procs[theProc0] += sumEntries
	procs[theProc] += sumEntries
	totEffAccNumer += sumEntries
    dataName = '%s_125_13TeV_NOTAG'%(nameMap[theProc0])
    sumEntries = theWS.data(dataName).sumEntries()
    stage0noTag[theProc0] += sumEntries
    procsNoTag[theProc] += sumEntries
    totEffAccDenom += sumEntries

  print '\n\n\nStage 1.2 fractions:'
  for proc,val in procs.iteritems():
    procTot = stage0procs[ proc.split('_')[0] ]+stage0noTag[proc.split('_')[0]]
    theFrac = (val+procsNoTag[proc]) / procTot
    effAcc  = val / (val + procsNoTag[proc]) 
    print 'total     for process %s is %1.4f [1fb-1]'%(proc,(val+procsNoTag[proc]))
    print 'fraction  for process %s is %1.4f'%(proc,theFrac)
    print 'eff x acc for process %s is %1.4f'%(proc,effAcc)
    print '\n'
  totEffAcc = totEffAccNumer / (totEffAccNumer + totEffAccDenom)
  print 'total eff x acc is %1.4f'%(totEffAcc)

  with open('jsons/granularEffAcc_%s.json'%(opts.ext), 'w') as outFile:
    for proc,val in procs.iteritems():
      for cat in cats:
        granularKey = '%s__%s'%(proc,cat)
        #granularEffAcc = granularMap[granularKey] / ( stage0procs[proc.split('_')[0]] + stage0noTag[proc.split('_')[0]] )
        granularEffAcc = granularMap[granularKey] / (val + procsNoTag[proc])
        if granularEffAcc < 0.: granularEffAcc = 0.
        outFile.write("%s %.6f \n"%(granularKey, granularEffAcc) )

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
