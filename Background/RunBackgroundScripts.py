# Script for running background fitting jobs for flashggFinalFit
import os
import sys
from optparse import OptionParser
from collections import OrderedDict as od

# Import tools
from tools.submissionTools import *
from commonTools import *
from commonObjects import *
from CollectModels import collect_models, create_empty_json

def get_options():
  parser = OptionParser()
  # Take inputs from a config file
  parser.add_option('--inputConfig', dest='inputConfig', default='', help="Name of input config file (if specified will ignore other options)")
  parser.add_option('--mode', dest='mode', default='std', help="Which script to run. Options: ['fTestOnly','fTestParallel','bkgPlotsOnly']")
  parser.add_option('--jobOpts', dest='jobOpts', default='', help="Additional options to add to job submission. For Condor separate individual options with a colon (specify all within quotes e.g. \"option_xyz = abc+option_123 = 456\")")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only") 
  parser.add_option('--fitType', dest='fitType', default='mgg', help="Fit type: mgg, mjj or 2D. (default: mgg)")
  parser.add_option('--mggLow', dest='mggLow', default=100, type='int', help="Lower mgg fit range (default: 100)")
  parser.add_option('--mggHigh', dest='mggHigh', default=180, type='int', help="Upper mgg fit range (default: 180)")
  parser.add_option('--mjjLow', dest='mjjLow', default=80, type='int', help="Lower mjj fit range (default: 80)")
  parser.add_option('--mjjHigh', dest='mjjHigh', default=190, type='int', help="Upper mjj fit range (default: 190)")
  parser.add_option('--noClean', dest='noClean', default=False, action="store_true", help="Do not clean up old ROOT files and plots. (default: False)")
  return parser.parse_args()

(opt,args) = get_options()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING BACKGROUND SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING BACKGROUND SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract options from config file
options = od()
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    #copy file to have common name and then import cfg options (dict)
    os.system("cp %s config.py"%opt.inputConfig)
    from config import backgroundScriptCfg
    _cfg = backgroundScriptCfg

    #Extract options
    options['dataFile']     = _cfg['inputWS']
    options['cats']         = _cfg['cats']
    options['catOffset']    = _cfg['catOffset']
    options['ext']          = _cfg['ext']
    options['year']         = _cfg['year']
    options['lumi']         = lumiMap[_cfg['year']]
    options['batch']        = _cfg['batch']
    options['queue']        = _cfg['queue']

    # Options from command line
    options['mode']                    = opt.mode
    options['jobOpts']                 = opt.jobOpts
    options['printOnly']               = opt.printOnly
    options['fitType']                 = opt.fitType
    options['mggLow']                 = opt.mggLow
    options['mggHigh']                = opt.mggHigh
    options['mjjLow']                 = opt.mjjLow
    options['mjjHigh']                = opt.mjjHigh
    options['noClean']                = opt.noClean

    # Delete copy of file
    os.system("rm config.py")

  else:
    print("[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig)
    leave()
else:
  print("[ERROR] Please specify config file to run from. Leaving..."%opt.inputConfig)
  leave()

# Check if mode is allowed in options
if options['mode'] not in ['fTestParallel']:
  print(" --> [ERROR] mode %s is not allowed. The only current supported mode is: [fTestParallel]. Leaving..."%options['mode'])
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING BACKGROUND SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Remove existing root files
if options["fitType"] == "2D" and options["mode"] == "fTestParallel":
  pattern = f"{bwd__}/outdir_{options['ext']}/CMS-*.root"
elif options["fitType"] == "mgg" and options["mode"] == "fTestParallel":
  pattern = f"{bwd__}/outdir_{options['ext']}/CMS-HGG*.root"
elif options["fitType"] == "mjj" and options["mode"] == "fTestParallel":
  pattern = f"{bwd__}/outdir_{options['ext']}/CMS-HBB*.root"
else:
  print(" --> Invalid fitType. Exiting to avoid accidental deletion.")
  sys.exit(1)
root_files = glob.glob(pattern)

if len(co.bwd__) < 5:  # change this number if needed
  print(" --> Directory name too short. Exiting to avoid accidental deletion.")
  leave()
if len(options["ext"]) == 0:
  print(" --> Extension name blank. Exiting to avoid accidental deletion.")
  leave()

if len(root_files) > 0:
  print(" --> Removing existing root files")
  for f in root_files:
    print(f"   --> Removing {f}")
    os.remove(f)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If cat == auto: extract list of categories from datafile
if options['cats'] == 'auto':
  options['cats'] = extractListOfCatsFromData(options['dataFile'])
options['nCats'] = len(options['cats'].split(","))

# Add dummy entries for procs and signalFitWSFile (used in old plotting script)
options['signalFitWSFile'] = 'none'
options['procs'] = 'none'
if options['year'] == 'combined': options['year'] = 'all'

# Print info to user
print(" --> Input data file: %s"%options['dataFile'])
print(" --> Categories: %s"%options['cats'])
print(" --> Extension: %s"%options['ext'])
print(" --> Category offset: %g"%options['catOffset'])
print(" --> Year: %s ::: Corresponds to intLumi = %s fb^-1"%(options['year'],options['lumi']))
print(" --> Fit type: %s"%options['fitType'])
print("")
print(" --> Job information:")
print("     * Batch: %s"%options['batch'])
print("     * Queue: %s"%options['queue'])
print("")
if options['mode'] == "fTestParallel": print(" --> Running background fTest (in parallel)...")
print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make directory to store job scripts and output
if not os.path.isdir("%s/outdir_%s"%(bwd__,options['ext'])): os.system("mkdir %s/outdir_%s"%(bwd__,options['ext']))

# Write submission files: style depends on batch system
writeSubFiles(options)
# if options['fitType'] == "mgg" or options['fitType'] == "2D":
#   writeSubFilesMgg(options)
# if options['fitType'] == "mjj" or options['fitType'] == "2D":
#   writeSubFilesMjj(options)
print("  --> Finished writing submission scripts")

# Submit scripts to batch system
if not options['printOnly']:
  submitFiles(options)
  # if options["fitType"] == "mgg" or options['fitType'] == "2D":
  #   submitFilesMgg(options)
  # if options["fitType"] == "mjj" or options['fitType'] == "2D":
  #   submitFilesMjj(options)
else:
  print("  --> Running with printOnly option. Will not submit scripts")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2D Model Construction
output_path_base = "%s/outdir_%s/"%(bwd__,options['ext'])
if options['fitType'] == "2D":
  print("  --> Running 2D model construction")
  if options['mode'] == "fTestParallel":
    collect_models(
      json_file=f"{output_path_base}/models.json",
      output_path=f"{output_path_base}/CMS-2D_multipdf_{options['ext']}_%CAT.root",
      ws_type="bkg-nonres",
      no_clear=options['noClean'],
    )
    print("  --> Finished collecting models")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
leave()
