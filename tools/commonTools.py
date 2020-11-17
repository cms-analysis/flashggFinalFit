import os, sys
import glob
import re
import ROOT
import math
from collections import OrderedDict as od
from commonObjects import *

# Function for iterating over ROOT argsets in workspace
def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

def extractWSFileNames( _inputWSDir ): 
  if not os.path.isdir(_inputWSDir):
    print " --> [ERROR] No such directory (%s)"
    return False
  return glob.glob("%s/output_*.root"%_inputWSDir)

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

def containsNOTAG( _listOfWSFileNames ):
  f0 = ROOT.TFile(_listOfWSFileNames[0]) 
  ws = f0.Get(inputWSName__)
  allData = ws.allData()
  for d in allData:
    if "NOTAG" in d.GetName(): return True
  return False

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

# Mapping of process to name in datacard
procToDatacardNameMap = od()
procToDatacardNameMap['GG2H'] = "ggH"
procToDatacardNameMap['VBF'] = "qqH"
procToDatacardNameMap['WH2HQQ'] = "WH_had"
procToDatacardNameMap["ZH2HQQ"] = "ZH_had"
procToDatacardNameMap["QQ2HLNU"] = "WH_lep"
procToDatacardNameMap["QQ2HLL"] = "ZH_lep"
procToDatacardNameMap["TTH"] = "ttH"
procToDatacardNameMap["BBH"] = "bbH"
procToDatacardNameMap["THQ"] = "tHq"
procToDatacardNameMap["THW"] = "tHW"
procToDatacardNameMap["TH"] = "tHq"
procToDatacardNameMap["GG2HQQ"] = "ggZH_had"
procToDatacardNameMap["GG2HLL"] = "ggZH_ll"
procToDatacardNameMap["GG2HNUNU"] = "ggZH_nunu"

def procToDatacardName( _proc ):
  k = _proc.split("_")[0]
  if k in procToDatacardNameMap: _proc = re.sub( k, procToDatacardNameMap[k], _proc )
  return _proc
