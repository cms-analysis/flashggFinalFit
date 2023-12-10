# Script for running background fitting jobs for flashggFinalFit
import os, sys
from optparse import OptionParser
from collections import OrderedDict as od

# Import tools
from tools.submissionTools import *
from commonTools import *
from commonObjects import *

def get_options():
  parser = OptionParser()
  # Take inputs from a config file
  parser.add_option('--inputConfig', dest='inputConfig', default='', help="Name of input config file (if specified will ignore other options)")
  parser.add_option('--mode', dest='mode', default='std', help="Which script to run. Options: ['fTest']")
  parser.add_option('--modeOpts', dest='modeOpts', default='', help="Additional options to add to command line when running scripts (specify all within quotes e.g. \"--XYZ ABC\")")
  parser.add_option('--jobOpts', dest='jobOpts', default='', help="Additional options to add to job submission. For Condor separate individual options with a colon (specify all within quotes e.g. \"option_xyz = abc+option_123 = 456\")")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only") 
  return parser.parse_args()

(opt,args) = get_options()
print(opt.modeOpts)

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING BACKGROUND SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING BACKGROUND SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract options from config file
options = od()
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    #copy file to have common name and then import cfg options (dict)
    #os.system("cp %s config.py"%opt.inputConfig)
    #from config import backgroundScriptCfg
    #_cfg = backgroundScriptCfg
    import imp
    config_module = imp.load_source("config_module", opt.inputConfig)
    _cfg = config_module.backgroundScriptCfg

    #Extract options
    options['inputWSFile']  = _cfg['inputWSFile']
    options['cats']         = _cfg['cats']
    options['ext']          = _cfg['ext']
    options['year']         = _cfg['year']
    options['lumi']         = lumiMap[_cfg['year']]
    options['batch']        = _cfg['batch']
    options['queue']        = _cfg['queue']

    # Options from command line
    options['mode']         = opt.mode
    options['modeOpts']     = opt.modeOpts
    options['jobOpts']      = opt.jobOpts
    options['printOnly']    = opt.printOnly

    # Delete copy of file
    #os.system("rm config.py")

  else:
    print "[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig
    leave()
else:
  print "[ERROR] Please specify config file to run from. Leaving..."%opt.inputConfig
  leave()

# Check if mode is allowed in options
if options['mode'] not in ['fTest']:
  print " --> [ERROR] mode %s is not allowed. The only current supported mode is: [fTest]. Leaving..."%options['mode']
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING BACKGROUND SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If cat == auto: extract list of categories from datafile
if options['cats'] == 'auto':
  options['cats'] = extractListOfCatsFromData(options['inputWSFile'])
  #options['cats'] = options['cats'].split(",")[-1]
  #print(options['cats'])
options['nCats'] = len(options['cats'].split(","))

# Print info to user
print " --> Input data file: %s"%options['inputWSFile']
print " --> Categories: %s"%options['cats']
print " --> Extension: %s"%options['ext']
print " --> Year: %s ::: Corresponds to intLumi = %s fb^-1"%(options['year'],options['lumi'])
print ""
print " --> Job information:"
print "     * Batch: %s"%options['batch']
print "     * Queue: %s"%options['queue']
print ""
if options['mode'] == "fTest": print " --> Running background fTest..."
print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make directory to store job scripts and output
print bwd__
if not os.path.isdir("%s/outdir_%s"%(bwd__,options['ext'])): os.system("mkdir %s/outdir_%s"%(bwd__,options['ext']))

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
