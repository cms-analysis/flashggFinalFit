# script to append a simple name of the process to the ROOT files from flashgg

import os, sys, re
from optparse import OptionParser
import glob

def get_options():
  parser = OptionParser()
  parser.add_option('--inputWSDir', dest='inputWSDir', default='', help='Input WS directory')
  parser.add_option('--dryRun', dest='dryRun', action='store_true', default=False, help='Just print the commands, do not rename files')
  return parser.parse_args()
(opt,args) = get_options() 

cmds = []

procmap = {"GluGluH":"GG2H", "VBFHToGG":"VBF", "VBFHiggs0": "VBF_ALT", "ttHJet":"TTH", "ttHiggs0":"TTH_ALT", "ZH_HToGG":"ZH", "ZHiggs0":"ZH_ALT", "WminusH":"WH_WM", "WplusH": "WH_WP", "WHiggs0":"WH_ALT"}

for fname in glob.glob("%s/output*M*.root"%opt.inputWSDir):
    #print "changing name to ",fname
    basename = fname.split(".root")[0]
    newbasename = basename.replace("-pythia8","_pythia8").replace("_M-","_M")
    p = re.compile("\S+Higgs(\S+)ToGG\S+")
    m = p.match(newbasename)
    altmodel = m.group(1) if m else ""
    #print newbasename, "  altmodel = ",altmodel
    proc = ""
    for prefix,suffix in procmap.iteritems():
        if prefix in fname:
            proc = suffix
            break
    newname = "%s_%s%s.root" % (newbasename,proc,altmodel)
    cmds.append("mv -i %s %s" % (fname,newname))
    if opt.dryRun:
        print cmds[-1]

if not opt.dryRun:
    for c in cmds:
        os.system(c)


                
        
