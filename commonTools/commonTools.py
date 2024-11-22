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
    print(" --> [ERROR] No such directory (%s)")
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

def extractListOfCatsFromHiggsDNAAllData( _fileName ):
  f = ROOT.TFile(_fileName)
  trees = f.Get(inputHiggsDNAAllData__)
  cats = []
  for key in trees.GetListOfKeys():
    c = key.GetName().split("Data_%s_"%sqrts__)[-1]
    cats.append(c)
  cats.sort()
  trees.Delete()
  f.Close()
  return ",".join(cats)


def getBinNameByHiggsDNANumber(key, myNumber):
    # Loop through the list of tuples in the specified key
    for entry in differentialProcTable_[key]:
        if entry[0] == myNumber:
            return entry[1]
    return None  # If myNumber isn't found

def extractListOfProcsFromHiggsDNASignal(_listOfSubDirectories, _variable, _inoutSplitting):
  procs = [] # ggh_in, ggh_out, etc.
  main_procs = [] # ggh, etc.
  for dName in _listOfSubDirectories:
    dName = dName.split("/")[-1]
    p = conversionTable_[dName.split("_")[0]]
    if p not in main_procs: 
      main_procs.append(p)
      if (_inoutSplitting) and (_variable == ''):
        # inclusive case
        procs.append(p+'_in')
        procs.append(p+'_out')
      if (_inoutSplitting) and (_variable != ''):
        # differential case
        for i, currentTuple in enumerate(differentialProcTable_[_variable]):
          currentBin = currentTuple[1]
          procs.append(p+'_'+currentBin)
      if not (_inoutSplitting) and (_variable == ''):
        # inclusive case with no inout splitting
        procs.append(p)
      if not (_inoutSplitting) and (_variable != ''):
        # differential case
        for i, currentTuple in enumerate(differentialProcTable_[_variable]):
          # Remove in/out label
          currentBin = "_".join(currentTuple[1].split("_")[:-1])
          procs.append(p+'_'+currentBin)
          
  return ",".join(procs)

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
  elif "ZH" in _fileName: p = "zh"
  elif "VH" in _fileName: p = "vh"
  elif "ttH" in _fileName: p = "tth"
  elif "THQ" in _fileName: p = "thq"
  elif "THW" in _fileName: p = "thw"
  elif "bbH" in _fileName: p = "bbh"
  else:
    print(" --> [ERROR]: cannot extract production mode from input file name. Please update tools.commonTools.signalFromFileName")
    exit(1)
  return p,d

def massFromFileName(_fileName):
  m = 125 #default
  if "_M" in _fileName:
    m = _fileName.split("_M")[-1].split("_")[0]
  return m

# Function for converting STXS process to production mode in dataset name
procToDataMap = od()
procToDataMap['GG2H'] = 'ggh'
procToDataMap['VBF'] = 'vbf'
procToDataMap['VH'] = 'vh'
procToDataMap['ggh'] = 'ggh'
procToDataMap['vbf'] = 'vbf'
procToDataMap['vh'] = 'vh'
procToDataMap['tth'] = 'tth'
procToDataMap['GG2H_in'] = 'ggh_in'
procToDataMap['VBF_in'] = 'vbf_in'
procToDataMap['VH_in'] = 'vh_in'
procToDataMap['GG2H_out'] = 'ggh_out'
procToDataMap['VBF_out'] = 'vbf_out'
procToDataMap['VH_out'] = 'vh_out'
procToDataMap['WH2HQQ'] = 'wh'
procToDataMap['ZH2HQQ'] = 'zh'
procToDataMap['QQ2HLNU'] = 'wh'
procToDataMap['QQ2HLL'] = 'zh'
#procToDataMap['TTH'] = 'tth'
procToDataMap['TTH_in'] = 'tth_in'
procToDataMap['TTH_out'] = 'tth_out'
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

def dataToProc( _d ):
  dataToProcMap = {v:k for k,v in procToDataMap.items()}
  if _d in dataToProcMap: return dataToProcMap[_d]
  else: return _d

# Mapping of process to name in datacard
procToDatacardNameMap = od()
procToDatacardNameMap['GG2H'] = "ggh"
procToDatacardNameMap['VBF'] = "vbf"
procToDatacardNameMap['ggh'] = "ggh"
procToDatacardNameMap['vbf'] = "vbf"
procToDatacardNameMap['tth'] = "tth"
procToDatacardNameMap['vh'] = "vh"
procToDatacardNameMap['GG2H_in'] = "ggh_in"
procToDatacardNameMap['VBF_out'] = "vbf_out"
procToDatacardNameMap['WH2HQQ'] = "WH_had"
procToDatacardNameMap["ZH2HQQ"] = "ZH_had"
procToDatacardNameMap["QQ2HLNU"] = "WH_lep"
procToDatacardNameMap["QQ2HLL"] = "ZH_lep"
procToDatacardNameMap["TTH"] = "tth"
procToDatacardNameMap["TTH_in"] = "tth_in"
procToDatacardNameMap["TTH_out"] = "tth_out"
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
