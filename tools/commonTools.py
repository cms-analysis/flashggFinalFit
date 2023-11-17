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
  print "hey ", _listOfWSFileNames
  for fName in _listOfWSFileNames:
<<<<<<< HEAD
    print fName, "HEY"
    p = fName.split("13TeV_")[1].split(".root")[0]
=======
    p = fName.split("pythia8_")[1].split(".root")[0]
>>>>>>> origin/dev_fggfinalfits_lite
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

def extractListOfCatsFromData( _fileName ):
  f = ROOT.TFile(_fileName)
  ws = f.Get(inputWSName__)
  allData = ws.allData()
  cats = []
  for d in allData:
    c = d.GetName().split("Data_%s_"%sqrts__)[-1]
    cats.append(c)
  cats.sort()
  ws.Delete()
  f.Close()
  return ",".join(cats)

def containsNOTAG( _listOfWSFileNames ):
  f0 = ROOT.TFile(_listOfWSFileNames[0]) 
  ws = f0.Get(inputWSName__)
  allData = ws.allData()
  for d in allData:
    if "NOTAG" in d.GetName(): return True
  return False

# Function to return signal production (and decay extension if required) from input file name
def signalFromFileName(_fileName):
  p, d = None, None
  if "ggZH" in _fileName:
    p = "ggzh"
    if "ZToLL" in _fileName: d = "_ZToLL"
    elif "ZToNuNu" in _fileName: d = "_ZToNuNu"
    else: d = "_ZToQQ"
  elif "GluGlu" in _fileName: p = "ggh"
  elif "VBF" in _fileName: p = "vbf"
  elif "WH" in _fileName: p = "wh"
  elif "Wminus" in _fileName: p = "wh"
  elif "Wplus" in _fileName: p = "wh"
  elif "ZH" in _fileName: p = "zh"
  elif "ttH" in _fileName: p = "tth"
  elif "THQ" in _fileName: p = "thq"
  elif "THW" in _fileName: p = "thw"
  elif "bbH" in _fileName: p = "bbh"
  else:
    print " --> [ERROR]: cannot extract production mode from input file name. Please update tools.commonTools.signalFromFileName"
    exit(1)
  if "JHUGen" in _fileName:
    if "0L1Zg" in _fileName:
      p += "_ALT_L1Zg"
    elif "0L1" in _fileName:
      p += "_ALT_L1"
    elif "0M" in _fileName:
      p += "_ALT_0M"
    elif "0PH" in _fileName:
      p += "_ALT_0PH"
    elif "0PM" in _fileName:
      p += "_ALT_0PM"
    else:
      print " --> [ERROR]: cannot extract production mode from input file name. Please update tools.commonTools.signalFromFileName"
      exit(1)
    if "f05ph0" in _fileName:
      p += "f05"
  return p,d

# Function to return mass from input file name
def massFromFileName(_fileName):
  m = None
  # to be done with regexp
  if "_M120_" in _fileName: m = 120
  elif "_M125_" in _fileName: m = 125
  elif "_M130_" in _fileName: m = 130
  else: 
    print " ---> [ERROR]: cannot extract mass from input file name. Please update tools.commonTools.massFromFileName"
  return m

# Function for converting STXS process to production mode in dataset name
procToDataMap = od()
procToDataMap['GG2H'] = 'ggh'
procToDataMap['VBF'] = 'vbf'
procToDataMap['VBF_ALT_0PM'] = 'vbf_ALT_0PM'
procToDataMap['VBF_ALT_0PH'] = 'vbf_ALT_0PH'
procToDataMap['VBF_ALT_0PHf05'] = 'vbf_ALT_0PHf05'
procToDataMap['VBF_ALT_0M'] = 'vbf_ALT_0M'
procToDataMap['VBF_ALT_0Mf05'] = 'vbf_ALT_0Mf05'
procToDataMap['VBF_ALT_L1'] = 'vbf_ALT_L1'
procToDataMap['VBF_ALT_L1f05'] = 'vbf_ALT_L1f05'
procToDataMap['VBF_ALT_L1Zg'] = 'vbf_ALT_L1Zg'
procToDataMap['VBF_ALT_L1Zgf05'] = 'vbf_ALT_L1Zgf05'
procToDataMap['VH'] = 'wzh'
procToDataMap['WMINUSH2HQQ'] = 'wh'
procToDataMap['WPLUSH2HQQ'] = 'wh'
procToDataMap['WH_ALT0L1f05ph0'] = 'wh_ALT_L1f05'
procToDataMap['WH_ALT0PHf05ph0'] = 'wh_ALT_0PHf05'
procToDataMap['WH_ALT0PH'] = 'wh_ALT_0PH'
procToDataMap['WH_ALT0PM'] = 'wh_ALT_0PM'
procToDataMap['ZH'] = 'zh'
procToDataMap['ZH_ALT0L1f05ph0'] = 'zh_ALT_L1f05'
procToDataMap['ZH_ALT0L1'] = 'zh_ALT_L1'
procToDataMap['ZH_ALT0L1Zgf05ph0'] = 'zh_ALT_L1Zgf05'
procToDataMap['ZH_ALT0L1Zg'] = 'zh_ALT_L1Zg'
procToDataMap['ZH_ALT0Mf05ph0'] = 'zh_ALT_0Mf05'
procToDataMap['ZH_ALT0M'] = 'zh_ALT_0M'
procToDataMap['ZH_ALT0PHf05ph0'] = 'zh_ALT_0PHf05'
procToDataMap['ZH_ALT0PH'] = 'zh_ALT_0PH'
procToDataMap['ZH_ALT0PM'] = 'zh_ALT_0PM'
procToDataMap['QQ2HLNU'] = 'wh'
procToDataMap['QQ2HLL'] = 'zh'
procToDataMap['TTH'] = 'tth'
procToDataMap['TTH_ALT0Mf05ph0'] = 'tth_ALT_0Mf05'
procToDataMap['TTH_ALT0M'] = 'tth_ALT_0M'
procToDataMap['TTH_ALT0PM'] = 'tth_ALT_0PM'
procToDataMap['BBH'] = 'bbh'
procToDataMap['THQ'] = 'thq'
procToDataMap['THW'] = 'thw'
procToDataMap['GG2HQQ'] = 'ggzh'
procToDataMap['GG2HLL'] = 'ggzh'
procToDataMap['GG2HNUNU'] = 'ggzh'
def procToData( _proc ):
  k = _proc
  if k in procToDataMap: _proc = re.sub( k, procToDataMap[k], _proc )
  return _proc

def dataToProc( _d ):
  dataToProcMap = {v:k for k,v in procToDataMap.iteritems()}
  if _d in dataToProcMap: return dataToProcMap[_d]
  else: return _d

# Mapping of process to name in datacard
procToDatacardNameMap = od()
procToDatacardNameMap['GG2H'] = "ggH"
procToDatacardNameMap['VBF'] = "qqH"
procToDatacardNameMap['VH'] = "vH"
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
