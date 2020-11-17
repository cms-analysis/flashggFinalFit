import os
import glob
import re
from commonObjects import *

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def writePreamble(_file):
  _file.write("#!/bin/bash\n")
  _file.write("ulimit -s unlimited\n")
  _file.write("set -e\n")
  _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
  _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
  _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
  _file.write("eval `scramv1 runtime -sh`\n")
  _file.write("cd %s\n"%swd__)
  _file.write("export PYTHONPATH=$PYTHONPATH:%s/tools:%s/tools\n\n"%(cwd__,swd__))

def writeCondorSub(_file,_exec,_queue,_nJobs,_jobOpts,doHoldOnFailure=True,doPeriodicRetry=True):
  _file.write("executable = %s.sh\n"%_exec)
  _file.write("arguments  = $(ProcId)\n")
  _file.write("output     = %s.$(ClusterId).$(ProcId).out\n"%_exec)
  _file.write("error      = %s.$(ClusterId).$(ProcId).err\n\n"%_exec)
  if _jobOpts != '':
    _file.write("# User specified job options\n")
    for jo in _jobOpts.split(":"): _file.write("%s\n"%jo)
    _file.write("\n")
  if doHoldOnFailure:
    _file.write("# Send the job to Held state on failure\n")
    _file.write("on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)\n\n")
  if doPeriodicRetry:
    _file.write("# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.\n")
    _file.write("periodic_release =  (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 600)\n\n")
  _file.write("+JobFlavour = \"%s\"\n"%_queue)
  _file.write("queue %g"%_nJobs)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeSubFiles(_opts):
  # Make directory to store sub files
  if not os.path.isdir("%s/outdir_%s"%(swd__,_opts['ext'])): os.system("mkdir %s/outdir_%s"%(swd__,_opts['ext']))
  if not os.path.isdir("%s/outdir_%s/%s"%(swd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s"%(swd__,_opts['ext'],_opts['mode']))
  if not os.path.isdir("%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode']))

  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  # Remove current job files
  if len(glob.glob("%s/*"%_jobdir)): os.system("rm %s/*"%_jobdir)
  
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_%s_%s"%(_opts['mode'],_opts['ext'])
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
    writePreamble(_f)

    # Write details depending on mode

    # For looping over proc x cat
    if( _opts['mode'] == "signalFit" )&( not _opts['groupSignalFitJobsByCat'] ):
      for pidx in range(_opts['nProcs']):
        for cidx in range(_opts['nCats']):
          pcidx = pidx*_opts['nCats']+cidx
          p,c = _opts['procs'].split(",")[pidx], _opts['cats'].split(",")[cidx]
          _f.write("if [ $1 -eq %g ]; then\n"%pcidx)
          _f.write("  python %s/scripts/signalFit.py --inputWSDir %s --ext %s --proc %s --cat %s --year %s --analysis %s --massPoints %s --scales \'%s\' --scalesCorr \'%s\' --scalesGlobal \'%s\' --smears \'%s\' %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],p,c,_opts['year'],_opts['analysis'],_opts['massPoints'],_opts['scales'],_opts['scalesCorr'],_opts['scalesGlobal'],_opts['smears'],_opts['modeOpts']))
          _f.write("fi\n")
   
    # For looping over categories
    elif( _opts['mode'] == "signalFit" )&( _opts['groupSignalFitJobsByCat'] ):
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f.write("if [ $1 -eq %g ]; then\n"%cidx)
        for pidx in range(_opts['nProcs']):
          p = _opts['procs'].split(",")[pidx]
          _f.write("  python %s/scripts/signalFit.py --inputWSDir %s --ext %s --proc %s --cat %s --year %s --analysis %s --massPoints %s --scales \'%s\' --scalesCorr \'%s\' --scalesGlobal \'%s\' --smears \'%s\' %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],p,c,_opts['year'],_opts['analysis'],_opts['massPoints'],_opts['scales'],_opts['scalesCorr'],_opts['scalesGlobal'],_opts['smears'],_opts['modeOpts']))
        _f.write("fi\n")

    elif _opts['mode'] == "calcPhotonSyst":
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f.write("if [ $1 -eq %g ]; then\n"%cidx)
        _f.write("  python %s/scripts/calcPhotonSyst.py --cat %s --procs %s --ext %s --inputWSDir %s --scales \'%s\' --scalesCorr \'%s\' --scalesGlobal \'%s\' --smears \'%s\' %s\n"%(swd__,c,_opts['procs'],_opts['ext'],_opts['inputWSDir'],_opts['scales'],_opts['scalesCorr'],_opts['scalesGlobal'],_opts['smears'],_opts['modeOpts']))
        _f.write("fi\n")

    elif _opts['mode'] == "fTest":
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f.write("if [ $1 -eq %g ]; then\n"%cidx)
        _f.write("  python %s/scripts/fTest.py --cat %s --procs %s --ext %s --inputWSDir %s %s\n"%(swd__,c,_opts['procs'],_opts['ext'],_opts['inputWSDir'],_opts['modeOpts']))
        _f.write("fi\n")

    elif _opts['mode'] == "packageSignal":
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f.write("if [ $1 -eq %g ]; then\n"%cidx)
        _f.write("  python %s/scripts/packageSignal.py --cat %s --outputExt %s --massPoints %s %s\n"%(swd__,c,_opts['ext'],_opts['massPoints'],_opts['modeOpts']))
        _f.write("fi\n")

    # For single script
    elif _opts['mode'] == 'getEffAcc':
      _f.write("python %s/scripts/getEffAcc.py --inputWSDir %s --ext %s --procs %s --massPoints %s %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],_opts['procs'],_opts['massPoints'],_opts['modeOpts']))
    elif _opts['mode'] == 'getDiagProc':
      _f.write("python %s/scripts/getDiagProc.py --inputWSDir %s --ext %s %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],_opts['modeOpts']))
      
    # Close .sh file
    _f.close()
    os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

    # Condor submission file
    _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
    if _opts['mode'] == "signalFit": 
      if( not _opts['groupSignalFitJobsByCat'] ): writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats']*_opts['nProcs'],_opts['jobOpts'])
      else: writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
    elif( _opts['mode'] == "calcPhotonSyst" )|( _opts['mode'] == "fTest" )|( _opts['mode'] == "packageSignal" ): writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
    elif( _opts['mode'] == "getEffAcc" )|( _opts['mode'] == "getDiagProc" ): writeCondorSub(_fsub,_executable,_opts['queue'],1,_opts['jobOpts'])
    _fsub.close()
    
  # SGE...
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    _executable = "sub_%s_%s"%(_opts['mode'],_opts['ext'])

    # Write details depending on mode

    # For separate submission file per process x category
    if( _opts['mode'] == "signalFit" )&( not _opts['groupSignalFitJobsByCat'] ):
      for pidx in range(_opts['nProcs']):
        for cidx in range(_opts['nCats']):
          pcidx = pidx*_opts['nCats']+cidx
          p,c = _opts['procs'].split(",")[pidx], _opts['cats'].split(",")[cidx]
          _f = open("%s/%s_%g.sh"%(_jobdir,_executable,pcidx),"w")
          writePreamble(_f)
          _f.write("python %s/scripts/signalFit.py --inputWSDir %s --ext %s --proc %s --cat %s --year %s --analysis %s --massPoints %s --scales \'%s\' --scalesCorr \'%s\' --scalesGlobal \'%s\' --smears \'%s\' %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],p,c,_opts['year'],_opts['analysis'],_opts['massPoints'],_opts['scales'],_opts['scalesCorr'],_opts['scalesGlobal'],_opts['smears'],_opts['modeOpts']))
          _f.close()
          os.system("chmod 775 %s/%s_%g.sh"%(_jobdir,_executable,pcidx))

    # For separate submission file per category
    elif( _opts['mode'] == "signalFit" )&( _opts['groupSignalFitJobsByCat'] ):
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
        writePreamble(_f)
        for pidx in range(_opts['nProcs']):
          p = _opts['procs'].split(",")[pidx]
          _f.write("python %s/scripts/signalFit.py --inputWSDir %s --ext %s --proc %s --cat %s --year %s --analysis %s --massPoints %s --scales \'%s\' --scalesCorr \'%s\' --scalesGlobal \'%s\' --smears \'%s\' %s\n\n"%(swd__,_opts['inputWSDir'],_opts['ext'],p,c,_opts['year'],_opts['analysis'],_opts['massPoints'],_opts['scales'],_opts['scalesCorr'],_opts['scalesGlobal'],_opts['smears'],_opts['modeOpts']))
        _f.close()
        os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

    elif _opts['mode'] == "calcPhotonSyst":
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
        writePreamble(_f)
        _f.write("python %s/scripts/calcPhotonSyst.py --cat %s --procs %s --ext %s --inputWSDir %s --scales \'%s\' --scalesCorr \'%s\' --scalesGlobal \'%s\' --smears \'%s\' %s\n"%(swd__,c,_opts['procs'],_opts['ext'],_opts['inputWSDir'],_opts['scales'],_opts['scalesCorr'],_opts['scalesGlobal'],_opts['smears'],_opts['modeOpts']))
        _f.close()
        os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

    elif _opts['mode'] == "fTest":
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
        writePreamble(_f)
        _f.write("python %s/scripts/fTest.py --cat %s --procs %s --ext %s --inputWSDir %s %s\n"%(swd__,c,_opts['procs'],_opts['ext'],_opts['inputWSDir'],_opts['modeOpts']))
        _f.close()
        os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

    elif _opts['mode'] == "packageSignal":
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
        writePreamble(_f)
        _f.write("python %s/scripts/packageSignal.py --cat %s --outputExt %s --massPoints %s %s\n"%(swd__,c,_opts['ext'],_opts['massPoints'],_opts['modeOpts']))
        _f.close()
        os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

    # For single submission file
    elif _opts['mode'] == "getEffAcc":
      _f = open("%s/%s.sh"%(_jobdir,_executable),"w")
      writePreamble(_f)
      _f.write("python %s/scripts/getEffAcc.py --inputWSDir %s --ext %s --procs %s --massPoints %s %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],_opts['procs'],_opts['massPoints'],_opts['modeOpts']))
      _f.close()
      os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))
    elif _opts['mode'] == "getDiagProc":
      _f = open("%s/%s.sh"%(_jobdir,_executable),"w")
      writePreamble(_f)
      _f.write("python %s/scripts/getDiagProc.py --inputWSDir %s --ext %s %s\n"%(swd__,_opts['inputWSDir'],_opts['ext'],_opts['modeOpts']))
      _f.close()
      os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

         
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for submitting files to batch system
def submitFiles(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_%s_%s"%(_opts['mode'],_opts['ext'])
    cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,swd__)
    run(cmdLine)
    print "  --> Finished submitting files"

  # SGE
  elif _opts['batch'] in ['IC','SGE']:
    _executable = "sub_%s_%s"%(_opts['mode'],_opts['ext'])

    # Extract job opts
    jobOptsStr = _opts['jobOpts']

    # For separate submission file per process x category
    if( _opts['mode'] == "signalFit" )&( not _opts['groupSignalFitJobsByCat'] ):
      for pidx in range(_opts['nProcs']):
        for cidx in range(_opts['nCats']):
          pcidx = pidx*_opts['nCats']+cidx
          _subfile = "%s/%s_%g"%(_jobdir,_executable,pcidx)
          cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
          run(cmdLine)
    # Separate submission per category  
    elif( _opts['mode'] == "packageSignal" )|( _opts['mode'] == "fTest" )|( _opts['mode'] == "calcPhotonSyst" )|(( _opts['mode'] == "signalFit" )&( _opts['groupSignalFitJobsByCat'] )):
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _subfile = "%s/%s_%s"%(_jobdir,_executable,c)
        cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
        run(cmdLine)
    # Single submission
    elif(_opts['mode'] == "getEffAcc")|(_opts['mode'] == "getDiagProc"):
      _subfile = "%s/%s"%(_jobdir,_executable)
      cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
      run(cmdLine)
    print "  --> Finished submitting files"
  
  # Running locally
  elif _opts['batch'] == 'local':
    _executable = "sub_%s_%s"%(_opts['mode'],_opts['ext'])
    # For separate submission file per process x category
    if( _opts['mode'] == "signalFit" )&( not _opts['groupSignalFitJobsByCat'] ):
      for pidx in range(_opts['nProcs']):
        for cidx in range(_opts['nCats']):
          pcidx = pidx*_opts['nCats']+cidx
          _subfile = "%s/%s_%g"%(_jobdir,_executable,pcidx)
          cmdLine = "bash %s.sh"%(_subfile)
          run(cmdLine)
    # Separate submission per category  
    elif( _opts['mode'] == "packageSignal" )|( _opts['mode'] == "fTest" )|( _opts['mode'] == "calcPhotonSyst" )|(( _opts['mode'] == "signalFit" )&( _opts['groupSignalFitJobsByCat'] )):
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _subfile = "%s/%s_%s"%(_jobdir,_executable,c)
        cmdLine = "bash %s.sh"%_subfile
        run(cmdLine)
    # Single submission
    elif(_opts['mode'] == "getEffAcc")|(_opts['mode'] == "getDiagProc"):
      _subfile = "%s/%s"%(_jobdir,_executable)
      cmdLine = "bash %s.sh"%_subfile
      run(cmdLine)
    print "  --> Finished running files"

 
