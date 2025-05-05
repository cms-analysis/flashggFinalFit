#!/usr/bin/env python3

# Script for submitting signal fitting jobs for finalfitslite
import os
import sys
from optparse import OptionParser
from collections import OrderedDict as od

# Import tools from ./tools
from commonTools import *
from commonObjects import *
from tools.submissionTools import *
from CollectModels import collect_models, create_empty_json

def get_options():
  parser = OptionParser()
  # Take inputs from config file
  parser.add_option('--inputConfig', dest='inputConfig', default='', help="Name of input config file (if specified will ignore other options)")
  parser.add_option('--mode', dest='mode', default='', help="Which script to run. Options: ['fTest','getDiagProc','calcPhotonSyst','signalFit','packageOnly','sigPlotsOnly']")
  parser.add_option('--modeOpts', dest='modeOpts', default='', help="Additional options to add to command line when running scripts (specify all within quotes e.g. \"--XYZ ABC\")")
  parser.add_option('--jobOpts', dest='jobOpts', default='', help="Additional options to add to job submission. For Condor separate individual options with a colon (specify all within quotes e.g. \"option_xyz = abc+option_123 = 456\")")
  parser.add_option('--groupSignalFitJobsByCat', dest='groupSignalFitJobsByCat', default=False, action="store_true", help="Option to group signalFit jobs by category")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only")
  parser.add_option('--fitType', dest='fitType', default='mgg', help="Fit type: mgg, mjj or 2D. (default: mgg)")
  parser.add_option('--mggLow', dest='mggLow', default=100, type='int', help="Lower mgg fit range (default: 100)")
  parser.add_option('--mggHigh', dest='mggHigh', default=180, type='int', help="Upper mgg fit range (default: 180)")
  parser.add_option('--mjjLow', dest='mjjLow', default=80, type='int', help="Lower mjj fit range (default: 80)")
  parser.add_option('--mjjHigh', dest='mjjHigh', default=190, type='int', help="Upper mjj fit range (default: 190)")
  parser.add_option('--noClean', dest='noClean', default=False, action="store_true", help="Do not clean up old ROOT files and plots. (default: False)")
  return parser.parse_args()
(opt,args) = get_options()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract options from config file:
options = od()
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    #copy file to have common name and then import cfg options (dict)
    os.system("cp %s config.py"%opt.inputConfig)
    from config import signalScriptCfg
    _cfg = signalScriptCfg

    #Extract options
    options['inputWSDir']   = _cfg['inputWSDir']
    options['procs']        = _cfg['procs']
    options['cats']         = _cfg['cats']
    options['ext']          = _cfg['ext']
    options['analysis']     = _cfg['analysis']
    options['year']         = _cfg['year']
    options['massPoints']   = _cfg['massPoints']
    options['scales']       = _cfg['scales']
    options['scalesCorr']   = _cfg['scalesCorr']
    options['scalesGlobal'] = _cfg['scalesGlobal']
    options['smears']       = _cfg['smears']
    options['batch']        = _cfg['batch']
    options['queue']        = _cfg['queue']
    # Options from command line
    options['mode']                    = opt.mode
    options['modeOpts']                = opt.modeOpts
    options['jobOpts']                 = opt.jobOpts
    options['groupSignalFitJobsByCat'] = opt.groupSignalFitJobsByCat
    options['printOnly']               = opt.printOnly
    options['fitType']                 = opt.fitType
    options['mggLow']                  = opt.mggLow
    options['mggHigh']                 = opt.mggHigh
    options['mjjLow']                  = opt.mjjLow
    options['mjjHigh']                 = opt.mjjHigh
    options['noClean']                 = opt.noClean
  
    #Delete copy of file
    os.system("rm config.py")
  
  else:
    print("[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig)
    leave()
else: 
  print("[ERROR] Please specify config file to run from. Leaving..."%opt.inputConfig)
  leave()

# Add more checks: allowed batches

# Check all processes and mass points exist

# Check if mode in allowed options
if options['mode'] not in ['fTest','getDiagProc','calcPhotonSyst','signalFit']:
  print(" --> [ERROR] mode %s not allowed. Please use one of the following: ['fTest','getDiagProc','calcPhotonSyst','signalFit']. Leaving..."%options['mode'])
  leave()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract list of filenames
WSFileNames = extractWSFileNames(options['inputWSDir'])
if not WSFileNames: leave()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If proc/cat == auto. Extract processes and categories
if options['procs'] == "auto":
  options['procs'] = extractListOfProcs(WSFileNames)
options['nProcs'] = len(options['procs'].split(","))

if options['cats'] == "auto":
  options['cats'] = extractListOfCats(WSFileNames)
options['nCats'] = len(options['cats'].split(","))

# Extract low and high MH values
mps = []
for mp in options['massPoints'].split(","): mps.append(int(mp))
options['massLow'], options['massHigh'] = '%s'%min(mps), '%s'%max(mps)

# print(info to user)
print(" --> Input flashgg ws dir: %s"%options['inputWSDir'])
print(" --> Processes: %s"%options['procs'])
print(" --> Categories: %s"%options['cats'])
print(" --> Mass points: %s --> Low = %s, High = %s"%(options['massPoints'],options['massLow'],options['massHigh']))
print(" --> Extension: %s"%options['ext'])
print(" --> Analysis: %s"%options['analysis'])
print(" --> Year: %s ::: Corresponds to intLumi = %.2f fb^-1"%(options['year'],lumiMap[options['year']]))
print(" --> Fit type: %s"%options['fitType'])
if options['mode'] in ['calcPhotonSyst']:
  print(" --> Photon shape systematics:")
  print("     * scales       = %s"%options['scales'])
  print("     * scalesCorr   = %s"%options['scalesCorr'])
  print("     * scalesGlobal = %s"%options['scalesGlobal'])
  print("     * smears       = %s"%options['smears'])
  print("")
if options['batch'] in ['condor','IC','SGE']:
  print(" --> Job information:")
  print("     * Batch: %s"%options['batch'])
  print("     * Queue: %s"%options['queue'])
  print("")
elif options['batch'] == "local":
  print(" --> Job information:")
  print("     * Running locally")
  print("")
if options['printOnly']:
  print(" --> PRINT ONLY (no submission)")
  print("")
if options['mode'] == "fTest": print(" --> Running signal fit fTest (determine number of gaussians for proc x cat x vertex scenario)...")
elif options['mode'] == "getDiagProc": print(" --> Getting diagonal process for each analysis category...")
elif options['mode'] == "calcPhotonSyst": print(" --> Calculating photon shape systematics...")
elif options['mode'] == "signalFit": print(" --> Performing signal fit...")
elif options['mode'] == "packageOnly": print(" --> Packaging signal fits (one file per category)...")
print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Remove old models.json file
_json_file = "%s/outdir_%s/signalFit/output/models.json"%(swd__,options['ext'])
if options["mode"] == "signalFit" and not options['noClean']:
  if os.path.exists(_json_file):
    print("  --> Removing old models.json file")
    os.remove(_json_file)
  else:
    print("  --> No old models.json file to remove")

if options['mode'] == "signalFit" and not os.path.exists(_json_file):
  print("  --> Creating empty models.json file")
  create_empty_json(_json_file)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make directory to store job scripts and output
if not os.path.isdir("%s/outdir_%s"%(swd__,options['ext'])): os.system("mkdir %s/outdir_%s"%(swd__,options['ext']))

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
if options['fitType'] == "2D":
  print("  --> Running 2D model construction")
  output_path_base = "%s/outdir_%s/signalFit/output"%(swd__,options['ext'])
  if options['mode'] == "fTestParallel":
    collect_models(
      json_file=f"{output_path_base}/models.json",
      output_path=f"{output_path_base}/CMS-2D_sigfit_{options['ext']}_%PROC_%YEAR_%CAT.root",
      ws_type="signal",
      no_clear=options['noClean'],
    )

leave()
