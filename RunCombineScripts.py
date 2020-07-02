# Script for submitting datacard creation and combine jobs for flashggFinalFit

import os, sys
from optparse import OptionParser

lumi = {'2016':'35.9', '2017':'41.5', '2018':'59.8'}

def get_options():
  parser = OptionParser()

  # Take inputs from a config file: if this is used then ignore all other options
  parser.add_option('--inputConfig', dest='inputConfig', default='', help="Name of input config file (if specified will ignore other options)")
  
  # Setup 
  parser.add_option('--analysis', dest='analysis', default='datacard', help="analysis option") 
  parser.add_option('--analysis_type', dest='analysis_type', default='', help="analysis type. For HHWWgg: Res, EFT, NMSSM") 
  parser.add_option('--FinalState', dest='FinalState', default='', help="Used for HHWWgg. Ex) qqlnu, lnulnu, qqqq") 
  parser.add_option('--HHWWggCatLabel', dest='HHWWggCatLabel', default='UnLabelled', help="Option to add to name of comine output files") 
  parser.add_option('--mode', dest='mode', default='datacard', help="Running mode. Options: [datacard,combine,combinePlots,effAcc,yields]")
  parser.add_option('--inputWSDir', dest='inputWSDir', default='/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights', help="Directory storing flashgg workspaces" )
  parser.add_option('--cats', dest='cats', default='UntaggedTag_0,VBFTag_0', help="Define categories")
  parser.add_option('--ext', dest='ext', default='test', help="Extension: has to match that used for signal and background modelling") 
  parser.add_option('--year', dest='year', default='2016', help="Dataset year")

  parser.add_option('--signalProcs', dest='signalProcs', default='all', help="Comma separated list of signal processes: used for defining signal in effAcc. Example for HIG-18-029 would be GG2H,VBF")

  parser.add_option('--doUEPS', dest='doUEPS', default=0, type='int', help='Do underlying event and parton shower systematics')

  #Photon shape systematics
  parser.add_option('--scales', dest='scales', default='HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB', help="Photon shape systematics: scales")
  parser.add_option('--scalesCorr', dest='scalesCorr', default='MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB', help="Photon shape systematics: scalesCorr")
  parser.add_option('--scalesGlobal', dest='scalesGlobal', default='NonLinearity:UntaggedTag_0:2,Geant4', help="Photon shape systematics: scalesGlobal")
  parser.add_option('--smears', dest='smears', default='HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho', help="Photon shape systematics: smears")

  # Options for running on the batch
  parser.add_option('--batch', dest='batch', default='IC', help="Batch")
  parser.add_option('--queue', dest='queue', default='hep.q', help="Queue")

  # Miscellaneous options
  parser.add_option('--printOnly', dest='printOnly', default=0, type='int', help="Dry run: print command only")
  parser.add_option('--doSystematics', dest='doSystematics', default='0', help="Queue")
  
  return parser.parse_args()

(opt,args) = get_options()

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING COMBINE SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IF using config file then extract options:
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    #copy file to have common name and then import cfg options (dict)
    os.system("cp %s config.py"%opt.inputConfig)
    from config import combineScriptCfg
    _cfg = combineScriptCfg

    #Extract options
    analysis     = _cfg['analysis']
    analysis_type = _cfg['analysis_type']
    FinalState   = _cfg['FinalState']
    HHWWggCatLabel = _cfg['HHWWggCatLabel']
    mode         = _cfg['mode']
    inputWSDir   = _cfg['inputWSDir']
    cats         = _cfg['cats']
    ext          = _cfg['ext']
    year         = _cfg['year']
    signalProcs  = _cfg['signalProcs']
    doUEPS       = _cfg['doUEPS']
    scales       = _cfg['scales']
    scalesCorr   = _cfg['scalesCorr']
    scalesGlobal = _cfg['scalesGlobal']
    smears       = _cfg['smears']
    batch        = _cfg['batch']
    queue        = _cfg['queue']
    printOnly    = opt.printOnly
    doSystematics= _cfg['doSystematics']

    #Delete copy of file
    os.system("rm config.py")

  else:
    print "[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING COMBINE SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    sys.exit(1)

#Else extract from option parser
else:
  analysis     = opt.analysis 
  analysis_type = opt.analysis_type
  FinalState   = opt.FinalState
  HHWWggCatLabel = opt.HHWWggCatLabel
  mode         = opt.mode
  inputWSDir   = opt.inputWSDir
  cats         = opt.cats
  ext          = opt.ext
  year         = opt.year
  signalProcs  = opt.signalProcs
  doUEPS       = opt.doUEPS
  scales       = opt.scales
  scalesCorr   = opt.scalesCorr
  scalesGlobal = opt.scalesGlobal
  smears       = opt.smears
  batch        = opt.batch
  queue        = opt.queue
  printOnly    = opt.printOnly
  doSystematics= opt.doSystematics

# Check if mode in allowed options
if mode not in ['datacard','combine','combinePlots','effAcc','yields']:
  print " --> [ERROR] mode %s not allowed. Please use one of the following: [datacard,combine,combinePlots,effAcc,yields]. Leaving..."
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract list of input ws filenames
ws_fileNames = []
for root, dirs, files in os.walk( inputWSDir ):
  for fileName in files:
    if (analysis != "HHWWgg") and not fileName.startswith('output_'): continue # relax constraint for HHWWgg due to different naming convention 
    if not fileName.endswith('.root'): continue
    ws_fileNames.append( fileName )

# print'ws_fileNames: ',ws_fileNames

# Extract string (list) of MH=125 filenames and also 120+130 for effAcc
ws_fullFileNames_125 = ''
ws_fullFileNames_effAcc = ''

if analysis == "HHWWgg":
  # concatenate with input dir to get full list of complete file names
  ws_fullFileNames = ''
  for fileName in ws_fileNames: ws_fullFileNames+="%s/%s,"%(inputWSDir,fileName)
  ws_fullFileNames = ws_fullFileNames[:-1]

else:
  for fileName in ws_fileNames:
    proc = fileName.split('pythia8_')[1].split('.root')[0]
    if 'M125' in fileName: 
      ws_fullFileNames_125 += "%s/%s,"%(inputWSDir,fileName)
      if signalProcs == 'all': ws_fullFileNames_effAcc += "%s/%s,"%(inputWSDir,fileName)
      else: 
        if proc in signalProcs.split(","): ws_fullFileNames_effAcc += "%s/%s,"%(inputWSDir,fileName)
    elif 'M120' in fileName or 'M130' in fileName:
      if signalProcs == 'all': ws_fullFileNames_effAcc += "%s/%s,"%(inputWSDir,fileName)
      else: 
        if proc in signalProcs.split(","): ws_fullFileNames_effAcc += "%s/%s,"%(inputWSDir,fileName)
  ws_fullFileNames_125 = ws_fullFileNames_125[:-1]
  ws_fullFileNames_effAcc = ws_fullFileNames_effAcc[:-1]

# print'ws_fullFileNames: ',ws_fullFileNames
# exit(0)

# For UE and PS uncertainties: add file names
ueps_fileNames = ''
if doUEPS:
  print " --> [ERROR] UE/PS uncertainties not yet configured!"
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  print sys.exit(1)

if analysis == "HHWWgg": procs = signalProcs

else: 
  # Extract list of procs
  procs = ''
  for fileName in ws_fileNames:
    if 'M125' not in fileName: continue
    procs += "%s,"%fileName.split('pythia8_')[1].split('.root')[0]
  procs = procs[:-1]

# Extract input files
dataFile = "%s/allData.root"%inputWSDir
signalFitWSFile = "%s/Signal/outdir_%s/CMS-HGG_sigfit_%s.root"%(os.environ['PWD'],ext,ext)
# Check if signal WS file exists
if not os.path.exists( signalFitWSFile ):
  print " --> [ERROR] signal fit workspace (%s) does not exist. Please run signal fitting first. Leaving..."%signalFitWSFile

# /afs/cern.ch/work/a/atishelm/private/CMSSW_10_2_13/src/flashggFinalFit/Signal/outdir_HHWWgg_v2-3_2017_X260_HHWWgg_qqlnu/CMS-HGG_sigfit_HHWWgg_v2-3_2017_X260_HHWWgg_qqlnu.root
# /afs/cern.ch/work/a/atishelm/private/CMSSW_10_2_13/src/flashggFinalFit/Signal/outdir_HHWWgg_v2-3_2017_X260_HHWWgg_qqlnu/CMS-HGG_mva_13TeV_sigfit.root

# /afs/cern.ch/work/a/atishelm/private/CMSSW_10_2_13/src/flashggFinalFit/Signal/outdir_HHWWgg_v2-3_2017/CMS-HGG_sigfit_HHWWgg_v2-3_2017.root

# Print info to user
print " --> Input flashgg ws dir: %s"%inputWSDir
print " --> Processes: %s"%procs
print " --> Categories: %s"%cats
print " --> Extension: %s"%ext
print " --> Year: %s ::: Corresponds to intLumi = %s fb^-1"%(year,lumi[year])
print " --> Signal processes (for eff x acc): %s"%signalProcs
if doUEPS: print " --> Calculating UE/PS systematics"
print ""
print " --> Photon shape systematics:"
print "     * scales       = %s"%scales
print "     * scalesCorr   = %s"%scalesCorr
print "     * scalesGlobal = %s"%scalesGlobal
print "     * smears       = %s"%smears
print ""
print " --> Job information:"
print "     * Batch: %s"%batch
print "     * Queue: %s"%queue
print ""
if mode == "datacard": print " --> Making datacard..."
elif mode == "combine": print " --> Running combine fits..."
elif mode == "combinePlots": print " --> Making plots from combine fits..."
elif mode == "effAcc": print " --> Making eff x acc plot..."
elif mode == "yields": print " --> Making yields table..."

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Construct input command
if mode not in ['effAcc','yields']:
  cmdLine = './runCombineScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --batch %s --dataFile %s --isData '%(ws_fullFileNames_125,procs,cats,ext,lumi[year],year,batch,dataFile)
  if mode == 'datacard': 
    # for HHWWgg analysis, need to create datacard for each mass point 
    if analysis == "HHWWgg": 
      filesList = ws_fullFileNames.split(',')
      for f in filesList:
        print
        print'On File: ',f
        print
        # ext = _HHWWgg_v2-3_2017_X280_WWgg_qqlnugg
        shortExt = "%s"%ext
        
        massExt = f.split('/')[-1].split('.')[0]
        thisExt = ext + '_' + massExt
        cmdLine = './runCombineScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --dataFile %s --isData --doSystematics %s --shortExt %s --HHWWggCatLabel %s '%(f,procs,cats,thisExt,lumi[year],year,dataFile,doSystematics,shortExt,HHWWggCatLabel)

        cmdLine += ' --datacardOnly --smears %s --scales %s --scalesCorr %s --scalesGlobal %s --analysis %s --verbose 1 --analysis_type %s --FinalState %s'%(smears,scales,scalesCorr,scalesGlobal,analysis,analysis_type,FinalState)
        print'cmdLine: ',cmdLine
        os.system( cmdLine )
    else: 
      cmdLine += '--datacardOnly --smears %s --scales %s --scalesCorr %s --scalesGlobal %s --doStage1 '%(smears,scales,scalesCorr,scalesGlobal)
    if doUEPS:
      cmdLine += ' --uepsFile '+uepsFileNames 
  elif mode == 'combine': 
    if analysis == "HHWWgg":
      filesList = ws_fullFileNames.split(',')
      for f in filesList:
        print
        print'On File: ',f
        print
        shortExt = "%s"%ext
        massExt = f.split('/')[-1].split('.')[0]
        thisExt = ext + '_' + massExt
        # print'shortExt:',shortExt
        cmdLine = './runCombineScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --dataFile %s --isData --analysis %s --shortExt %s --HHWWggCatLabel %s --analysis_type %s --FinalState %s'%(f,procs,cats,ext,lumi[year],year,dataFile,analysis,shortExt,HHWWggCatLabel,analysis_type,FinalState)
        cmdLine += ' --combineOnly '
        print'cmdLine: ',cmdLine
        os.system( cmdLine )
    else:
      cmdLine += ' --combineOnly '
  elif mode == 'combinePlots': cmdLine += '--combinePlotsOnly '

elif mode == 'effAcc': cmdLine = './makeStage1EffAcc.py -i %s -s Signal/outdir_%s/sigfit/effAccCheck_all.root -p %s -c %s'%(ws_fullFileNames_effAcc,ext,procs,cats)

elif mode == 'yields': cmdLine = './stage1yields.py -w %s -p %s -s Signal/signumbers_%s.txt -u Background/CMS-HGG_multipdf_%s.root --intLumi %s -c %s'%(ws_fullFileNames_125,procs,ext,ext,lumi[year],cats)

if analysis != "HHWWgg":
  # Either print command to screen or run
  if printOnly: print "\n%s"%cmdLine
  else: os.system( cmdLine )

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
