#!/usr/bin/env python

# Script for submitting worksapce related jobs for finalfitslite
import os, sys
from optparse import OptionParser
from collections import OrderedDict as od

# Import tools from ./tools
from commonTools import *
from commonObjects import *
from tools.submissionTools import *

def get_options():
  parser = OptionParser()
  # Take inputs from config file
  parser.add_option('--inputDir', dest='inputDir', default='', help="Path to input trees (for trees2ws + hadding) orpath to input workspaces (for mass_shift)")
  parser.add_option('--inputConfig', dest='inputConfig', default='', help="Name of input config file for trees2ws/trees2ws_data")
  parser.add_option('--ext', dest='ext', default='test_2016', help="Extension to add to output jobs dir")
  parser.add_option('--year', dest='year', default='2016', help="Year of trees to process")
  parser.add_option('--mode', dest='mode', default='', help="Which mode to run. Options: ['trees2ws','trees2ws_data','haddMC','haddData','mass_shift']")
  parser.add_option('--modeOpts', dest='modeOpts', default='', help="Additional options to add to command line when running different scripts (specify all within quotes e.g. \"--XYZ ABC\")")
  # Specifically for hadding
  parser.add_option('--flashggPath', dest='flashggPath', default='', help="Path to flashgg area required for hadding")
  parser.add_option('--outputWSDir', dest='outputWSDir', default='', help="Location to store output workspaces of hadding script")
  # Specifically for mass shifting
  parser.add_option('--inputMass', dest='inputMass', default='125', help="Input mass of workspace")
  parser.add_option('--targetMasses', dest='targetMasses', default='120,130', help="Comma separated list of target masses")
  # Job submission options
  parser.add_option('--batch', dest='batch', default='IC', help='Batch')
  parser.add_option('--queue', dest='queue', default='hep.q', help='Queue: can take a while if including all systematics for many categories')
  parser.add_option('--jobOpts', dest='jobOpts', default='', help="Additional options to add to job submission. For Condor separate individual options with a colon (specify all within quotes e.g. \"option_xyz = abc+option_123 = 456\")")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only")
  return parser.parse_args()
(opt,args) = get_options()

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING WS SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING WS SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract options from config file:
options = od()
options['inputDir']    = opt.inputDir
options['inputConfig'] = opt.inputConfig
options['ext']         = opt.ext
options['year']        = opt.year
options['mode']        = opt.mode
options['modeOpts']    = opt.modeOpts
options['flashggPath'] = opt.flashggPath
options['outputWSDir'] = opt.outputWSDir if opt.outputWSDir != '' else "%s/outdir_%s/%s"%(twd__,opt.ext,opt.mode)
options['inputMass']   = opt.inputMass
options['targetMasses']   = opt.targetMasses
options['batch']       = opt.batch
options['queue']       = opt.queue
options['jobOpts']     = opt.jobOpts
options['printOnly']   = opt.printOnly

# Check if mode in allowed options
if options['mode'] not in ['trees2ws','trees2ws_data','haddMC','haddData','mass_shift']:
  print " --> [ERROR] mode %s not allowed. Please use one of the following: ['trees2ws','trees2ws_data','haddMC','haddData','mass_shift']. Leaving..."%options['mode']
  leave()

# print info to user
print " --> Input directory: %s"%options['inputDir']
print " --> Year: %s"%(options['year'])
if options['mode'] in ['trees2ws','trees2ws_data']:
  print " --> Input config: %s"%options['inputConfig']
if options['mode'] in ['haddMC']:
  print " --> flashgg path: %s"%options['flashggPath']
  print " --> Output RooWorkspace directory: %s"%options['outputWSDir']

if options['mode'] == "trees2ws": print " --> Converting ROOT Trees to FinalFits compatible RooWorkspace for MC..."
elif options['mode'] == "trees2ws_data": print " --> Converting ROOT Trees to FinalFits compatible RooWorkspace for data..."
elif options['mode'] == "haddMC": print " --> Hadd MC workspaces..."
elif options['mode'] == "haddData": print " --> Hadd data workspaces..."
elif options['mode'] == "mass_shift": print " --> Ad-hoc shifting of mass in RooWorkspaces..."
print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make directory to store job scripts and output
if not os.path.isdir("%s/outdir_%s"%(twd__,options['ext'])): os.system("mkdir %s/outdir_%s"%(twd__,options['ext']))

# Write submission files: style depends on batch system
writeSubFiles(options)
print "  --> Finished writing submission scripts"

# Submit scripts to batch system
if not options['printOnly']:
  submitFiles(options)
else:
  print "  --> Running with printOnly option. Will not submit scripts"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
leave()

