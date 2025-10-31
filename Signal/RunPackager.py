# Script for submitting packager for signal models
import os, sys
import glob
from optparse import OptionParser
from collections import OrderedDict as od

# Import tools from ./tools
from commonTools import *
from commonObjects import *
from tools.submissionTools import *

def get_options():
  parser = OptionParser()
  parser.add_option('--cats', dest='cats', default='auto', help="Comma separated list of categories. auto = automatically inferred from inputWSDir")
  parser.add_option("--inputWSDir", dest='inputWSDir', default='', help="Input flashgg WS directory: used for auto option")
  parser.add_option('--exts', dest='exts', default='', help="Comma separated lists of exts to merge")
  parser.add_option('--outputExt', dest='outputExt', default='packaged', help="Output extension")
  parser.add_option("--massPoints", dest='massPoints', default='120,125,130', help="Comma separated list of mass points")
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Use if merging categories across years")
  parser.add_option('--year', dest='year', default='2022preEE', help="If not merging then add year tag to file name")
  parser.add_option('--batch', dest='batch', default='condor', help='Batch')
  parser.add_option('--queue', dest='queue', default='espresso', help='Queue: should not take long (microcentury will do)')
  parser.add_option('--jobOpts', dest='jobOpts', default='', help="Additional options to add to job submission. For Condor separate individual options with a colon (specify all within quotes e.g. \"option_xyz = abc+option_123 = 456\")")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only")
  return parser.parse_args()
(opt,args) = get_options()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING PACKAGER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING PACKAGER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)

# Store all opts in orderedDict for submissionTools
options = od()
options['inputWSDir'] = opt.inputWSDir
options['cats'] = opt.cats
options['ext'] = opt.outputExt
options['massPoints'] = opt.massPoints
options['mode'] = 'packageSignal'
options['modeOpts'] = '--exts %s'%opt.exts
if opt.mergeYears:  options['modeOpts'] += ' --mergeYears'
else: options['modeOpts'] += ' --year %s'%opt.year
options['batch'] = opt.batch
options['queue'] = opt.queue
options['jobOpts'] = opt.jobOpts
options['printOnly'] = opt.printOnly
options['groupSignalFitJobsByCat'] = False # dummy

# Extract cats from input workspace dir
if options['cats'] == "auto":
  WSFileNames = extractWSFileNames(options['inputWSDir'])
  options['cats'] = extractListOfCats(WSFileNames)
options['nCats'] = len(options['cats'].split(","))

print(" --> Packaging signal workspaces from: %s"%opt.exts)
print(" --> For analysis categories: %s"%options['cats'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make directory to store job scripts and output
if not os.path.isdir("%s/outdir_%s"%(swd__,options['ext'])): os.system("mkdir %s/outdir_%s"%(swd__,options['ext']))

# Write submission files: style depends on batch system
writeSubFiles(options)
print("  --> Finished writing submission scripts")

# Submit scripts to batch system
if not options['printOnly']:
  submitFiles(options)
else:
  print("  --> Running with printOnly option. Will not submit scripts")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
leave()
