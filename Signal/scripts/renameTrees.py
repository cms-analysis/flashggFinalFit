# script to append a simple name of the process to the ROOT files from flashgg

import os, sys
from optparse import OptionParser
import glob

def get_options():
  parser = OptionParser()
  parser.add_option('--inputWSDir', dest='inputWSDir', default='', help='Input WS directory')
  parser.add_option('--dryRun', dest='dryRun', action='store_true', default=False, help='Just print the commands, do not rename files')
  return parser.parse_args()
(opt,args) = get_options() 

cmds = []

procmap = {"GluGluH":"GG2H", "VBFHToGG":"VBF", "VBFHiggs0": "VBF_ALT", "ttH":"TTH", "ggZH":"ZH", "WminusH":"WH_WM2ALL", "WplusH": "WH_WP2ALL", "VHToGG":"VH_V2ALL"}

for fname in glob.glob("%s/output*M*.root"%opt.inputWSDir):
    #print "changing name to ",fname
    basename = fname.split(".root")[0]
    newbasename = basename.replace("-pythia8","_pythia8")
    pythiaver = newbasename.split("_pythia8")[1]
    if pythiaver!="": 
        newbasename = newbasename.replace("_pythia8"+pythiaver,"_pythia8")
    proc = ""
    for prefix,suffix in procmap.iteritems():
        if prefix in fname:
            proc = suffix
            break
    newname = "%s_%s.root" % (newbasename,suffix)
    cmds.append("mv -i %s %s" % (fname,newname))
    if opt.dryRun:
        print cmds[-1]

if not opt.dryRun:
    for c in cmds:
        os.system(c)


                
        
