#!/usr/bin/env python
# code to make first-pass stxs transfer matrix plots

from os import listdir
import ROOT as r
r.gROOT.SetBatch(True)
from collections import OrderedDict as od

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-e', '--ext', default='test', help='name of analysis')
parser.add_option('-f', '--filePath', default='test', help='directory of files')
parser.add_option('-c', '--cats', default='test', help='analysis categories')
(opts,args) = parser.parse_args()

baseFilePath  = opts.filePath
if not baseFilePath.endswith('/'): baseFilePath += '/'

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

stage0noTag = {}
stage0noTag['GG2H']    = 0.
stage0noTag['VBF']     = 0.
stage0noTag['WH2HQQ']  = 0.
stage0noTag['ZH2HQQ']  = 0.
stage0noTag['QQ2HLL']  = 0.
stage0noTag['QQ2HLNU'] = 0.
stage0noTag['TTH'] = 0.
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
    print 'processing %s'%theProc
    theFile = r.TFile(fileName, 'READ')
    theWS = theFile.Get('tagsDumper/cms_hgg_13TeV')
    for cat in cats:
      dataName = '%s_125_13TeV_%s'%(nameMap[theProc0], cat)
      sumEntries = theWS.data(dataName).sumEntries()
      granularKey = '%s__%s'%(theProc,cat)
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

  print '\n\n\nStage 1.1 fractions:'
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
        granularKey = '%s__%s'%(theProc,cat)
        granularEffAcc = granularMap[granularKey] / ( stage0procs[proc.split('_')[0]] + stage0noTag[proc.split('_')[0]] )
        if granularEffAcc < 0.: granularEffAcc = 0.
        outFile.write(" '%s' : %.6f , \n"%(granularKey, granularEffAcc) )
    outFile.write(" 'fino' : 'alla fine' ")

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
