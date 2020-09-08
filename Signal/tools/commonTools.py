import os
import glob
import re
import ROOT
from collections import OrderedDict as od
from commonStrings import *

def extractWSFileNames( _inputWSDir ): return glob.glob("%s/output_*.root"%_inputWSDir)

def extractListOfProcs( _listOfWSFileNames ):
  procs = []
  for fName in _listOfWSFileNames:
    p = fName.split("pythia8_")[1].split(".root")[0]
    if p not in procs: procs.append(p)
  return ",".join(procs)

def extractListOfCats( _listOfWSFileNames ):
  f0 = ROOT.TFile(_listOfWSFileNames[0]) 
  ws = f0.Get(inputWSName__)
  allData = ws.allData()
  cats = []
  for d in allData:
    # Skip systematics shifts
    if "sigma" in d.GetName(): continue
    # Skip NOTAG
    elif "NOTAG" in d.GetName(): continue
    # Add to list: name of the form {proc}_{mass}_{sqrts}_{cat}
    cats.append(d.GetName().split("_%s_"%sqrts__)[-1])
  ws.Delete()
  f0.Close()
  return ",".join(cats)

# Function for converting STXS process to production mode in dataset name
procToDataMap = od()
procToDataMap['GG2H'] = 'ggh'
procToDataMap['VBF'] = 'vbf'
procToDataMap['WH2HQQ'] = 'wh'
procToDataMap['ZH2HQQ'] = 'zh'
procToDataMap['QQ2HLNU'] = 'wh'
procToDataMap['QQ2HLL'] = 'zh'
procToDataMap['TTH'] = 'tth'
procToDataMap['BBH'] = 'bbh'
procToDataMap['THQ'] = 'thq'
procToDataMap['THW'] = 'thw'
procToDataMap['GG2HQQ'] = 'ggzh'
procToDataMap['GG2HLL'] = 'ggzh'
procToDataMap['GG2HNUNU'] = 'ggzh'
def procToData( _proc ):
  k = _proc.split("_")[0]
  if k in procToDataMap: _proc = re.sub( k, procToDataMap[k], _proc )
  return _proc
