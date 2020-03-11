# Script for submitting signal fitting jobs for flashggFinalFit

import os, sys
from optparse import OptionParser

lumi = {'2016':'35.9', '2017':'41.5', '2018':'59.8'}

def finishCommand(cmdLine_,useDCB_,mode_,printOnly_):
  if useDCB_: cmdLine_ += ' --useDCB_1G 1'
  else: cmdLine_ += ' --useDCB_1G 0'
  if mode_ == "phoSystCalc": cmdLine_ += ' --calcPhoSystOnly' 
  elif mode_ == "sigFitOnly": cmdLine_ += ' --sigFitOnly --dontPackage' 
  elif mode_ == "packageOnly": cmdLine_ += ' --packageOnly'
  elif mode_ == "sigPlotsOnly": cmdLine_ += ' --sigPlotsOnly'

  # Either print command to screen or run
  if printOnly_: print "\n%s"%cmdLine_
  else: os.system( cmdLine_ )

def get_options():
  parser = OptionParser()

  # Take inputs from a config file: if this is used then ignore all other options
  parser.add_option('--inputConfig', dest='inputConfig', default='', help="Name of input config file (if specified will ignore other options)")

  # Setup
  parser.add_option('--inputWSDir', dest='inputWSDir', default='/eos/home-j/jlangfor/hgg/ws/test_legacy_runII_102x', help="Directory storing flashgg workspaces" )
  parser.add_option('--cats', dest='cats', default='UntaggedTag_0,VBFTag_0', help="Define categories")
  parser.add_option('--usrprocs', dest='usrprocs', default='', help="Define production categories")
  parser.add_option('--ext', dest='ext', default='test', help="Extension: defines output dir where signal models are saved")
  parser.add_option('--analysis', dest='analysis', default='test', help="Analysis handle: used in Signal/python/replacementMap.py to specify replacement dataset mapping when too few entries")
  parser.add_option('--year', dest='year', default='2016', help="Dataset year")
  parser.add_option('--beamspot', dest='beamspot', default='3.4', help="Beamspot")
  parser.add_option('--numberOfBins', dest='numberOfBins', default='320', help="Number of bins in mgg to fit")

  #Use DCB in fit
  parser.add_option('--useDCB', dest='useDCB', default=0, type='int', help="Use DCB in signal fit [yes=1,no=0(default)]")

  #Mass points
  parser.add_option('--massPoints', dest='massPoints', default='120,125,130', help="Mass points to fit") 

  #Photon shape systematics
  parser.add_option('--scales', dest='scales', default='HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB', help="Photon shape systematics: scales")
  parser.add_option('--scalesCorr', dest='scalesCorr', default='MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB', help="Photon shape systematics: scalesCorr")
  parser.add_option('--scalesGlobal', dest='scalesGlobal', default='NonLinearity:UntaggedTag_0:2,Geant4', help="Photon shape systematics: scalesGlobal")
  parser.add_option('--smears', dest='smears', default='HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho', help="Photon shape systematics: smears")

  # Options for running on the batch
  parser.add_option('--batch', dest='batch', default='HTCONDOR', help="Batch")
  parser.add_option('--queue', dest='queue', default='espresso', help="Queue")

  # Miscellaneous options: only performing a single function 
  parser.add_option('--mode', dest='mode', default='std', help="Allows single function [std,phoSystOnly,sigFitOnly,packageOnly,sigPlotsOnly]")
  parser.add_option('--printOnly', dest='printOnly', default=0, type='int', help="Dry run: print command only")
  parser.add_option('--verbosity', dest='verbosity', default=0, type='int', help="verbosity")
  # parser.add_option('--runLocal', dest='runLocal', default=0, type='int', help="Run locally, no batch systems")
  # parser.add_option('--HHWWgg', dest='HHWWgg', default=0, type='int', help="(0): Do not run for HHWWgg analysis (1): Run for HHWWgg analysis ")
  return parser.parse_args()

(opt,args) = get_options()

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IF using config file then extract options:
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    #copy file to have common name and then import cfg options (dict)
    os.system("cp %s config.py"%opt.inputConfig)
    from config import signalScriptCfg
    _cfg = signalScriptCfg

    #Extract options
    inputWSDir   = _cfg['inputWSDir']
    cats         = _cfg['cats']
    usrprocs     = _cfg['usrprocs']
    ext          = _cfg['ext']
    analysis     = _cfg['analysis']
    year         = _cfg['year']
    beamspot     = _cfg['beamspot']
    numberOfBins = _cfg['numberOfBins']
    useDCB       = _cfg['useDCB']
    massPoints   = _cfg['massPoints']
    scales       = _cfg['scales']
    scalesCorr   = _cfg['scalesCorr']
    scalesGlobal = _cfg['scalesGlobal']
    smears       = _cfg['smears']
    batch        = _cfg['batch']
    queue        = _cfg['queue']
    mode         = _cfg['mode']
    printOnly    = opt.printOnly # Still take printOnly from options
    verbosity      = _cfg['verbosity']
    # runLocal     = _cfg['runLocal']
    # HHWWgg       = _cfg['HHWWgg']
  
    #Delete copy of file
    os.system("rm config.py")
  
  else:
    print "[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    sys.exit(1)

#Else extract from option parser
else:
  inputWSDir   = opt.inputWSDir
  cats         = opt.cats
  usrprocs     = opt.usrprocs
  ext          = opt.ext
  analysis     = opt.analysis
  year         = opt.year
  beamspot     = opt.beamspot
  numberOfBins = opt.numberOfBins
  useDCB       = opt.useDCB
  massPoints   = opt.massPoints
  scales       = opt.scales
  scalesCorr   = opt.scalesCorr
  scalesGlobal = opt.scalesGlobal
  smears       = opt.smears
  batch        = opt.batch
  queue        = opt.queue
  mode         = opt.mode
  printOnly    = opt.printOnly
  verbosity      = opt.verbosity
  # runLocal     = opt.runLocal
  # HHWWgg       = opt.HHWWgg

# Check if mode in allowed options
if mode not in ['std','calcPhotonSyst','writePhotonSyst','sigFitOnly','packageOnly','sigPlotsOnly']:
  print " --> [ERROR] mode %s not allowed. Please use one of the following: [std,phoSystOnly,sigFitOnly,packageOnly,sigPlotsOnly]. Leaving..."%mode
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)  

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FIXME: configure also for CONDOR
# If mode == calcPhotonSyst: submit a job to the batch for each category
if mode == "calcPhotonSyst":
  print " --> Calculating photon systematics: %s"%ext
  if not os.path.isdir("./outdir_%s"%ext): os.system("mkdir ./outdir_%s"%ext)
  if not os.path.isdir("./outdir_%s/calcPhotonSyst"%ext): os.system("mkdir ./outdir_%s/calcPhotonSyst"%ext)
  if not os.path.isdir("./outdir_%s/calcPhotonSyst/jobs"%ext): os.system("mkdir ./outdir_%s/calcPhotonSyst/jobs"%ext)
  # Write submission scripts
  for cat_idx in range(len(cats.split(","))):
    cat = cats.split(",")[cat_idx]
    f = open("./outdir_%s/calcPhotonSyst/jobs/sub%g.sh"%(ext,cat_idx),"w")
    f.write("#!/bin/bash\n\n")
    f.write("cd %s/src/flashggFinalFit/Signal\n\n"%os.environ['CMSSW_BASE']) 
    f.write("eval `scramv1 runtime -sh`\n\n")
    f.write("python python/calcPhotonSyst.py --cat %s --ext %s --inputWSDir %s --scales %s --scalesCorr %s --scalesGlobal %s --smears %s"%(cat,ext,inputWSDir,scales,scalesCorr,scalesGlobal,smears))
    f.close()
  # If not printOnly: submit submission scripts to batch
  if not printOnly:
    for cat_idx in range(len(cats.split(","))):
      cat = cats.split(",")[cat_idx]
      print " --> Category: %s (sub%g.sh)"%(cat,cat_idx)
      os.system("qsub -q hep.q -l h_rt=0:20:0 ./outdir_%s/calcPhotonSyst/jobs/sub%g.sh"%(ext,cat_idx))

elif mode == "writePhotonSyst":
  print " --> Write photon systematics to .dat file compatible with SignalFit.cpp: %s"%ext
  os.system("eval `scramv1 runtime -sh`; python python/writePhotonSyst.py --cats %s --ext %s --scales %s --scalesCorr %s --scalesGlobal %s --smears %s"%(cats,ext,scales,scalesCorr,scalesGlobal,smears)) 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
else:
  # Extract list of input ws filenames
  ws_fileNames = []
  for root, dirs, files in os.walk( inputWSDir ):
    # print'files = ',files 
    for fileName in files:
      # if not fileName.startswith('output_'): continue # remove requirement of output_ string for HHWWgg files 
      if not fileName.endswith('.root'): continue
      ws_fileNames.append( fileName )
      # print'fileName: ',fileName 
  # concatenate with input dir to get full list of complete file names
  ws_fullFileNames = ''
  for fileName in ws_fileNames: ws_fullFileNames+="%s/%s,"%(inputWSDir,fileName)
  ws_fullFileNames = ws_fullFileNames[:-1]

  # Extract list of procs
  procs = ''

  # If user input list of procs exists
  nUsrProcs = len(usrprocs.split(","))
  if nUsrProcs > 0:
    for proc_idx in range(nUsrProcs):
      proc = usrprocs.split(",")[proc_idx]
      # print'proc = ',proc 
      procs += proc 
    # if nUsrProcs > 1:
    # procs = procs[:-1]

  # otherwise get from files 
  else:
    for fileName in ws_fileNames:
      if 'M125' not in fileName: continue
      procs += "%s,"%fileName.split('pythia8_')[1].split('.root')[0]
    procs = procs[:-1]    

  # Extract low and high MH values
  mps = []
  for mp in massPoints.split(","): mps.append(int(mp))
  mass_low, mass_high = '%s'%min(mps), '%s'%max(mps)

  # print info to user
  print " --> Input flashgg ws dir: %s"%inputWSDir
  print " --> Processes: %s"%procs
  print " --> Categories: %s"%cats
  print " --> Mass points: %s --> Low = %s, High = %s"%(massPoints,mass_low,mass_high)
  print " --> Extension: %s"%ext
  print " --> Analysis: %s"%analysis
  print " --> Year: %s ::: Corresponds to intLumi = %s fb^-1"%(year,lumi[year])
  if useDCB: print " --> Using DCB in signal model"
  # print " --> HHWWgg: %s"%HHWWgg
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
  if mode == "phoSystCalc": print " --> Calculating photon systematics only..."
  elif mode == "sigFitOnly": print " --> Running signal fit only..."
  elif mode == "packageOnly": print " --> Packaging only..."
  elif mode == "sigPlotsOnly": print " --> Running the signal plotting scripts only..."
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

  # Construct input command
  print " --> Constructing the input command..."

  cmdLine = ''
  # origext = ext 

  # if analysis is HHWWgg, need to run process for each mass point...this will need to be updated when we add a second category
  if analysis == 'HHWWgg':
    # print'ws_fullFileNames: ',ws_fullFileNames
    filesList = ws_fullFileNames.split(',')
    for f in filesList:
      cmdLine = ''
      print
      print'On File: ',f
      print
      # ext = _HHWWgg_v2-3_2017_X280_WWgg_qqlnugg
      
      massExt = f.split('/')[-1].split('.')[0]
      thisExt = ext + '_' + massExt

      # if batch not specified, run locally 
      if batch == '': cmdLine += './runSignalScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --massList %s --bs %s --analysis %s --scales %s --scalesCorr %s --scalesGlobal %s --smears %s --useSSF 1 --verbosity %s '%(f,procs,cats,thisExt,lumi[year],year,massPoints,beamspot,analysis,scales,scalesCorr,scalesGlobal,smears,verbosity)

      # run with batch 
      else: cmdLine += './runSignalScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --batch %s --queue %s --massList %s --bs %s --analysis %s --scales %s --scalesCorr %s --scalesGlobal %s --smears %s --useSSF 1 --verbosity %s'%(f,procs,cats,thisExt,lumi[year],year,batch,queue,massPoints,beamspot,analysis,scales,scalesCorr,scalesGlobal,smears,verbosity)
    
      finishCommand(cmdLine,useDCB,mode,printOnly)

  # non-HHWWgg analysis 
  else:
    cmdLine = ''
    # if batch not specified, run locally 
    if batch == '': cmdLine += './runSignalScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --massList %s --bs %s --analysis %s --scales %s --scalesCorr %s --scalesGlobal %s --smears %s --useSSF 1 --verbosity %s '%(ws_fullFileNames,procs,cats,ext,lumi[year],year,massPoints,beamspot,analysis,scales,scalesCorr,scalesGlobal,smears,verbosity)

    # run with batch 
    else: cmdLine += './runSignalScripts.sh -i %s -p %s -f %s --ext %s --intLumi %s --year %s --batch %s --queue %s --massList %s --bs %s --analysis %s --scales %s --scalesCorr %s --scalesGlobal %s --smears %s --useSSF 1 --verbosity %s'%(ws_fullFileNames,procs,cats,ext,lumi[year],year,batch,queue,massPoints,beamspot,analysis,scales,scalesCorr,scalesGlobal,smears,verbosity)
    
    finishCommand(cmdLine,useDCB,mode,printOnly)

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING SIGNAL SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
