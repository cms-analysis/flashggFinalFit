print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FITTER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import ROOT
import pandas as pd
import pickle
import os, sys
from optparse import OptionParser
import glob
import re
from collections import OrderedDict as od

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FITTER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option("--proc", dest='proc', default='', help="Signal process")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option('--massPoints', dest='massPoints', default='120,125,130', help="Mass points to fit")
  parser.add_option("--inputWSDir", dest='inputWSDir', default='', help="Input flashgg WS directory")
  parser.add_option("--useDCB", dest='useDCB', default=False, action="store_true", help="Use DCB in signal fitting")
  return parser.parse_args()
(opt,args) = get_options()

# Function for converting STXS process to production mode in dataset name
def procToData( _proc ):
  proc_map = {"GG2H":"ggh","VBF":"vbf","WH2HQQ":"wh","ZH2HQQ":"zh","QQ2HLNU":"wh","QQ2HLL":"zh","TTH":"tth","BBH":"bbh","THQ":"thq","THW":"thw","TH":"thq","GG2HQQ":"ggzh","GG2HLL":"ggzh","GG2HNUNU":"ggzh"}
  for key in proc_map: 
    if key == _proc.split("_")[0]: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

# Extract inputWSFiles
print " --> Taking signal workspaces from directory: %s"%opt.inputWSDir
if not os.path.isdir( opt.inputWSDir ):
  print " --> [ERROR] Directory %s does not exist. Leaving"%opt.inputWSDir
  leave()
# Glob output worksapces
fnames = glob.glob("%s/output*"%opt.inputWSDir)
inputWSFiles = od()
for fname in fnames:
  # Extract process name
  _proc = re.sub(".root","",fname.split("pythia8_")[-1])
  _massPoint = fname.split("_")[fname.split("_").index("13TeV")-1][1:]
  _nominalDataName = "%s_%s_13TeV_%s"%(procToData(_proc.split("_")[0]),_massPoint,opt.cat)
  if(_proc == opt.proc)&(_massPoint in opt.massPoints.split(",")):
    inputWSFiles["%s_%s"%(_proc,_massPoint)] = {
      "name":fname,
      "nominalDataName":_nominalDataName,
      "massPoint":_massPoint
    }

# Loop over input files
for k,iWSF in inputWSFiles.iteritems():
  # Open ROOT file and extract nominal dataset
  f = ROOT.TFile(iWSF['name'])
  iWS = f.Get("tagsDumper/cms_hgg_13TeV")
  d = iWS.data(iWSF['nominalDataName'])

  print " --> Successfully extract dataset: %s. Number of entries = %g"%(d.GetName(),d.numEntries())

  # Extract mass variable
  

  # Delete WS and close file
  iWS.Delete()
  f.Close() 
