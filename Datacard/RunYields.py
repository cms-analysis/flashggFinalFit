# Script for submitting packager for signal models
import os, sys
import glob
from optparse import OptionParser
from collections import OrderedDict as od

# Import tools
from commonTools import *
from commonObjects import *
from tools.submissionTools import *

def get_options():
  parser = OptionParser()
  # Input details
  parser.add_option('--cats', dest='cats', default='auto', help="Comma separated list of categories. auto = automatically inferred from inputWSDirMap")
  parser.add_option('--inputParquetDirMap', dest='inputParquetDirMap', default='2016=/vols/cms/jl2117/hgg/ws/UL/Sept20/MC_final/signal_2016', help="Map. Format: year=inputWSDir (separate years by comma)")
  parser.add_option('--procs', dest='procs', default='auto', help='Comma separated list of signal processes. auto = automatically inferred from input workspaces')
  parser.add_option('--ext', dest='ext', default='test', help='Extension for saving')
  parser.add_option('--mass', dest='mass', default='125', help='Input workspace mass')
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Merge category across years")
  parser.add_option('--skipBkg', dest='skipBkg', default=False, action="store_true", help="Only add signal processes to datacard")
  parser.add_option('--bkgScaler', dest='bkgScaler', default=1., type="float", help="Add overall scale factor for background")
  parser.add_option('--sigModelWSDir', dest='sigModelWSDir', default='./Models/signal', help='Input signal model WS directory')
  parser.add_option('--sigModelExt', dest='sigModelExt', default='packaged', help='Extension used when saving signal model')
  parser.add_option('--bkgModelWSDir', dest='bkgModelWSDir', default='./Models/background', help='Input background model WS directory')
  parser.add_option('--bkgModelExt', dest='bkgModelExt', default='multipdf', help='Extension used when saving background model')
  # For yields calculations:
  parser.add_option('--skipZeroes', dest='skipZeroes', default=False, action="store_true", help="Skip signal processes with 0 sum of weights")
  # For systematics:
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--ignore-warnings', dest='ignore_warnings', default=False, action="store_true", help="Skip errors for missing systematics. Instead output warning message")
  # For submission
  parser.add_option('--batch', dest='batch', default='condor', help='Batch')
  parser.add_option('--queue', dest='queue', default='3600', help='Queue: should not take long (microcentury will do)')
  parser.add_option('--jobOpts', dest='jobOpts', default='', help="Additional options to add to job submission. For Condor separate individual options with a colon (specify all within quotes e.g. \"option_xyz = abc+option_123 = 456\")")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only")
  return parser.parse_args()
(opt,args) = get_options()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING YIELDS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING YIELDS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)

# Store all opts in orderedDict for submissionTools
options = od()
options['cats'] = opt.cats
options['inputParquetDirMap'] = opt.inputParquetDirMap
options['procs'] = opt.procs
options['ext'] = opt.ext
options['mass'] = opt.mass
options['sigModelWSDir'] = opt.sigModelWSDir
options['sigModelExt'] = opt.sigModelExt
options['bkgModelWSDir'] = opt.bkgModelWSDir
options['bkgModelExt'] = opt.bkgModelExt
options['modeOpts'] = ''
if opt.mergeYears:  options['modeOpts'] += ' --mergeYears'
if opt.skipBkg: options['modeOpts'] += ' --skipBkg'
if opt.bkgScaler != 1.: options['modeOpts'] += ' --bkgScaler %.4f'%opt.bkgScaler
if opt.skipZeroes: options['modeOpts'] += ' --skipZeroes'
if opt.doSystematics: options['modeOpts'] += ' --doSystematics'
if opt.ignore_warnings: options['modeOpts'] += ' --ignore-warnings'
options['batch'] = opt.batch
options['queue'] = opt.queue
options['jobOpts'] = opt.jobOpts
options['printOnly'] = opt.printOnly


options['nCats'] = len(options['cats'].split(","))
print(" --> Running yields for following cats: %s"%options['cats'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make directory to store job scripts and output
if not os.path.isdir("%s/yields_%s"%(dwd__,options['ext'])): os.system("mkdir %s/yields_%s"%(dwd__,options['ext']))

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
