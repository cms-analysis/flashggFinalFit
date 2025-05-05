import os
import glob
import re
from commonObjects import *

def run(cmd):
  print("%s\n\n"%cmd)
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
def writeCondorSubFilesMgg(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  _executable = "condor_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])
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
        _f.write(
            f"  python3 {swd__}/scripts/signalFit.py " +
            f"--inputWSDir {_opts['inputWSDir']} " +
            f"--ext {_opts['ext']} " +
            f"--proc {p} " +
            f"--cat {c} " +
            f"--year {_opts['year']} " +
            f"--analysis {_opts['analysis']} " +
            f"--massPoints {_opts['massPoints']} " +
            f"--scales '{_opts['scales']}' " +
            f"--scalesCorr '{_opts['scalesCorr']}' " +
            f"--scalesGlobal '{_opts['scalesGlobal']}' " +
            f"--smears '{_opts['smears']}' " +
            f"--weightName {_opts['weightName']} " +
            f"--mggLow {_opts['mggLow']} " +
            f"--mggHigh {_opts['mggHigh']} " +
            f"{_opts['modeOpts']}\n"
        )
        _f.write("fi\n")
  
  # For looping over categories
  elif( _opts['mode'] == "signalFit" )&( _opts['groupSignalFitJobsByCat'] ):
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      for pidx in range(_opts['nProcs']):
        p = _opts['procs'].split(",")[pidx]
        _f.write( 
          f"  python3 {swd__}/scripts/signalFit.py " +
          f"--inputWSDir {_opts['inputWSDir']} " +
          f"--ext {_opts['ext']} " +
          f"--proc {p} " +
          f"--cat {c} " +
          f"--year {_opts['year']} " +
          f"--analysis {_opts['analysis']} " +
          f"--massPoints {_opts['massPoints']} " +
          f"--scales '{_opts['scales']}' " +
          f"--scalesCorr '{_opts['scalesCorr']}' " +
          f"--scalesGlobal '{_opts['scalesGlobal']}' " +
          f"--smears '{_opts['smears']}' " +
          f"--weightName {_opts['weightName']} " +
          f"--mggLow {_opts['mggLow']} " +
          f"--mggHigh {_opts['mggHigh']} " +
          f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == "calcPhotonSyst":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write(
        f"  python3 {swd__}/scripts/calcPhotonSyst.py " +
        f"--cat {c} " +
        f"--procs {_opts['procs']} " +
        f"--ext {_opts['ext']} " +
        f"--inputWSDir {_opts['inputWSDir']} " +
        f"--scales '{_opts['scales']}' " +
        f"--scalesCorr '{_opts['scalesCorr']}' " +
        f"--scalesGlobal '{_opts['scalesGlobal']}' " +
        f"--smears '{_opts['smears']}' " +
        f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == "fTest":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write(
        f"  python3 {swd__}/scripts/fTest.py " +
        f"--cat {c} " +
        f"--procs {_opts['procs']} " +
        f"--ext {_opts['ext']} " +
        f"--inputWSDir {_opts['inputWSDir']} " +
        f"--weightName {_opts['weightName']} " +
        f"--mggLow {_opts['mggLow']} " +
        f"--mggHigh {_opts['mggHigh']} " +
        f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == "packageSignal":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write(
        f"  python3 {swd__}/scripts/packageSignal.py " +
        f"--cat {c} " +
        f"--outputExt {_opts['ext']} " +
        f"--massPoints {_opts['massPoints']} " +
        f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == 'getDiagProc':
    _f.write(
      f"python3 {swd__}/scripts/getDiagProc.py " +
      f"--inputWSDir {_opts['inputWSDir']} " +
      f"--ext {_opts['ext']} " +
      f"{_opts['modeOpts']}\n"
    )
    
  # Close .sh file
  _f.close()
  os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

  # Condor submission file
  _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
  if _opts['mode'] == "signalFit": 
    if( not _opts['groupSignalFitJobsByCat'] ): 
      writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats']*_opts['nProcs'],_opts['jobOpts'])
    else: 
      writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
  elif( _opts['mode'] == "calcPhotonSyst" )|( _opts['mode'] == "fTest" )|( _opts['mode'] == "packageSignal" ): 
    writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
  _fsub.close()


def writeCondorSubFilesMjj(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  _executable = "condor_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])
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
        _f.write(
            f"  python3 {swd__}/scripts/signalFitMjj.py " +
            f"--inputWSDir {_opts['inputWSDir']} " +
            f"--ext {_opts['ext']} " +
            f"--proc {p} " +
            f"--cat {c} " +
            f"--year {_opts['year']} " +
            f"--analysis {_opts['analysis']} " +
            f"--massPoints {_opts['massPoints']} " +
            f"--scales '{_opts['scales']}' " +
            f"--scalesCorr '{_opts['scalesCorr']}' " +
            f"--scalesGlobal '{_opts['scalesGlobal']}' " +
            f"--smears '{_opts['smears']}' " +
            f"--weightName {_opts['weightName']} " +
            f"--mjjLow {_opts['mjjLow']} " +
            f"--mjjHigh {_opts['mjjHigh']} " +
            f"{_opts['modeOpts']}\n"
        )
        _f.write("fi\n")
  
  # For looping over categories
  elif( _opts['mode'] == "signalFit" )&( _opts['groupSignalFitJobsByCat'] ):
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      for pidx in range(_opts['nProcs']):
        p = _opts['procs'].split(",")[pidx]
        _f.write( 
          f"  python3 {swd__}/scripts/signalFitMjj.py " +
          f"--inputWSDir {_opts['inputWSDir']} " +
          f"--ext {_opts['ext']} " +
          f"--proc {p} " +
          f"--cat {c} " +
          f"--year {_opts['year']} " +
          f"--analysis {_opts['analysis']} " +
          f"--massPoints {_opts['massPoints']} " +
          f"--scales '{_opts['scales']}' " +
          f"--scalesCorr '{_opts['scalesCorr']}' " +
          f"--scalesGlobal '{_opts['scalesGlobal']}' " +
          f"--smears '{_opts['smears']}' " +
          f"--weightName {_opts['weightName']} " +
          f"--mjjLow {_opts['mjjLow']} " +
          f"--mjjHigh {_opts['mjjHigh']} " +
          f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == "calcPhotonSyst": # TODO
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write(
        f"  python3 {swd__}/scripts/calcPhotonSyst.py " +
        f"--cat {c} " +
        f"--procs {_opts['procs']} " +
        f"--ext {_opts['ext']} " +
        f"--inputWSDir {_opts['inputWSDir']} " +
        f"--scales '{_opts['scales']}' " +
        f"--scalesCorr '{_opts['scalesCorr']}' " +
        f"--scalesGlobal '{_opts['scalesGlobal']}' " +
        f"--smears '{_opts['smears']}' " +
        f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == "fTest":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write(
        f"  python3 {swd__}/scripts/fTestMjj.py " +
        f"--cat {c} " +
        f"--procs {_opts['procs']} " +
        f"--ext {_opts['ext']} " +
        f"--inputWSDir {_opts['inputWSDir']} " +
        f"--weightName {_opts['weightName']} " +
        f"--mjjLow {_opts['mjjLow']} " +
        f"--mjjHigh {_opts['mjjHigh']} " +
        f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == "packageSignal": # TODO
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write(
        f"  python3 {swd__}/scripts/packageSignal.py " +
        f"--cat {c} " +
        f"--outputExt {_opts['ext']} " +
        f"--massPoints {_opts['massPoints']} " +
        f"{_opts['modeOpts']}\n")
      _f.write("fi\n")

  elif _opts['mode'] == 'getDiagProc': # TODO
    _f.write(
      f"python3 {swd__}/scripts/getDiagProc.py " +
      f"--inputWSDir {_opts['inputWSDir']} " +
      f"--ext {_opts['ext']} " +
      f"{_opts['modeOpts']}\n"
    )
    
  # Close .sh file
  _f.close()
  os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

  # Condor submission file
  _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
  if _opts['mode'] == "signalFit": 
    if( not _opts['groupSignalFitJobsByCat'] ): 
      writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats']*_opts['nProcs'],_opts['jobOpts'])
    else: 
      writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
  elif( _opts['mode'] == "calcPhotonSyst" )|( _opts['mode'] == "fTest" )|( _opts['mode'] == "packageSignal" ): 
    writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
  _fsub.close()
  pass

def writeSGESubFilesMgg(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  _executable = "sub_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])

  # Write details depending on mode

  # For separate submission file per process x category
  if( _opts['mode'] == "signalFit" )&( not _opts['groupSignalFitJobsByCat'] ):
    for pidx in range(_opts['nProcs']):
      for cidx in range(_opts['nCats']):
        pcidx = pidx*_opts['nCats']+cidx
        p,c = _opts['procs'].split(",")[pidx], _opts['cats'].split(",")[cidx]
        _f = open("%s/%s_%g.sh"%(_jobdir,_executable,pcidx),"w")
        writePreamble(_f)
        _f.write(
            f"python3 {swd__}/scripts/signalFit.py " +
            f"--inputWSDir {_opts['inputWSDir']} " +
            f"--ext {_opts['ext']} " +
            f"--proc {p} " +
            f"--cat {c} " +
            f"--year {_opts['year']} " +
            f"--analysis {_opts['analysis']} " +
            f"--massPoints {_opts['massPoints']} " +
            f"--scales '{_opts['scales']}' " +
            f"--scalesCorr '{_opts['scalesCorr']}' " +
            f"--scalesGlobal '{_opts['scalesGlobal']}' " +
            f"--smears '{_opts['smears']}' " +
            f"--weightName {_opts['weightName']} " +
            f"--mggLow {_opts['mggLow']} " +
            f"--mggHigh {_opts['mggHigh']} " +
            f"{_opts['modeOpts']}\n"
        )
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
        _f.write(
            f"python3 {swd__}/scripts/signalFit.py " +
            f"--inputWSDir {_opts['inputWSDir']} " +
            f"--ext {_opts['ext']} " +
            f"--proc {p} " +
            f"--cat {c} " +
            f"--year {_opts['year']} " +
            f"--analysis {_opts['analysis']} " +
            f"--massPoints {_opts['massPoints']} " +
            f"--scales '{_opts['scales']}' " +
            f"--scalesCorr '{_opts['scalesCorr']}' " +
            f"--scalesGlobal '{_opts['scalesGlobal']}' " +
            f"--smears '{_opts['smears']}' " +
            f"--weightName {_opts['weightName']} " +
            f"--mggLow {_opts['mggLow']} " +
            f"--mggHigh {_opts['mggHigh']} " +
            f"{_opts['modeOpts']}\n\n"
        )
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  elif _opts['mode'] == "calcPhotonSyst":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write("python3 " +
           f"{swd__}/scripts/calcPhotonSyst.py " +
           f"--cat {c} " +
           f"--procs {_opts['procs']} " +
           f"--ext {_opts['ext']} " +
           f"--inputWSDir {_opts['inputWSDir']} " +
           f"--scales '{_opts['scales']}' " +
           f"--scalesCorr '{_opts['scalesCorr']}' " +
           f"--scalesGlobal '{_opts['scalesGlobal']}' " +
           f"--smears '{_opts['smears']}' " +
           f"{_opts['modeOpts']}\n")
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  elif _opts['mode'] == "fTest":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write(
          f"python3 {swd__}/scripts/fTest.py " +
          f"--cat {c} " +
          f"--procs {_opts['procs']} " +
          f"--ext {_opts['ext']} " +
          f"--inputWSDir {_opts['inputWSDir']} " +
          f"--weightName {_opts['weightName']} " +
          f"--mggLow {_opts['mggLow']} " +
          f"--mggHigh {_opts['mggHigh']} " +
          f"{_opts['modeOpts']}\n"
      )
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  elif _opts['mode'] == "packageSignal":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write(
          f"python3 {swd__}/scripts/packageSignal.py " +
          f"--cat {c} " +
          f"--outputExt {_opts['ext']} " +
          f"--massPoints {_opts['massPoints']} " +
          f"{_opts['modeOpts']}\n"
      )
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  # For single submission file
  elif _opts['mode'] == "getDiagProc":
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w")
    writePreamble(_f)
    _f.write(
      f"python3 {swd__}/scripts/getDiagProc.py " +
      f"--inputWSDir {_opts['inputWSDir']} " +
      f"--ext {_opts['ext']} " +
      f"{_opts['modeOpts']}\n"
    )
    _f.close()
    os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

def writeSGESubFilesMjj(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  _executable = "sub_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])

  # Write details depending on mode

  # For separate submission file per process x category
  if( _opts['mode'] == "signalFit" )&( not _opts['groupSignalFitJobsByCat'] ):
    for pidx in range(_opts['nProcs']):
      for cidx in range(_opts['nCats']):
        pcidx = pidx*_opts['nCats']+cidx
        p,c = _opts['procs'].split(",")[pidx], _opts['cats'].split(",")[cidx]
        _f = open("%s/%s_%g.sh"%(_jobdir,_executable,pcidx),"w")
        writePreamble(_f)
        _f.write(
            f"python3 {swd__}/scripts/signalFitMjj.py " +
            f"--inputWSDir {_opts['inputWSDir']} " +
            f"--ext {_opts['ext']} " +
            f"--proc {p} " +
            f"--cat {c} " +
            f"--year {_opts['year']} " +
            f"--analysis {_opts['analysis']} " +
            f"--massPoints {_opts['massPoints']} " +
            f"--scales '{_opts['scales']}' " +
            f"--scalesCorr '{_opts['scalesCorr']}' " +
            f"--scalesGlobal '{_opts['scalesGlobal']}' " +
            f"--smears '{_opts['smears']}' " +
            f"--weightName {_opts['weightName']} " +
            f"--mjjLow {_opts['mjjLow']} " +
            f"--mjjHigh {_opts['mjjHigh']} " +
            f"{_opts['modeOpts']}\n"
        )
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
        _f.write(
            f"python3 {swd__}/scripts/signalFitMjj.py " +
            f"--inputWSDir {_opts['inputWSDir']} " +
            f"--ext {_opts['ext']} " +
            f"--proc {p} " +
            f"--cat {c} " +
            f"--year {_opts['year']} " +
            f"--analysis {_opts['analysis']} " +
            f"--massPoints {_opts['massPoints']} " +
            f"--scales '{_opts['scales']}' " +
            f"--scalesCorr '{_opts['scalesCorr']}' " +
            f"--scalesGlobal '{_opts['scalesGlobal']}' " +
            f"--smears '{_opts['smears']}' " +
            f"--weightName {_opts['weightName']} " +
            f"--mjjLow {_opts['mjjLow']} " +
            f"--mjjHigh {_opts['mjjHigh']} " +
            f"{_opts['modeOpts']}\n\n"
        )
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  elif _opts['mode'] == "calcPhotonSyst": # TODO
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write("python3 " +
           f"{swd__}/scripts/calcPhotonSyst.py " +
           f"--cat {c} " +
           f"--procs {_opts['procs']} " +
           f"--ext {_opts['ext']} " +
           f"--inputWSDir {_opts['inputWSDir']} " +
           f"--scales '{_opts['scales']}' " +
           f"--scalesCorr '{_opts['scalesCorr']}' " +
           f"--scalesGlobal '{_opts['scalesGlobal']}' " +
           f"--smears '{_opts['smears']}' " +
           f"{_opts['modeOpts']}\n")
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  elif _opts['mode'] == "fTest":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write(
          f"python3 {swd__}/scripts/fTestMjj.py " +
          f"--cat {c} " +
          f"--procs {_opts['procs']} " +
          f"--ext {_opts['ext']} " +
          f"--inputWSDir {_opts['inputWSDir']} " +
          f"--weightName {_opts['weightName']} " +
          f"--mjjLow {_opts['mjjLow']} " +
          f"--mjjHigh {_opts['mjjHigh']} " +
          f"{_opts['modeOpts']}\n"
      )
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  elif _opts['mode'] == "packageSignal": # TODO
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write(
          f"python3 {swd__}/scripts/packageSignal.py " +
          f"--cat {c} " +
          f"--outputExt {_opts['ext']} " +
          f"--massPoints {_opts['massPoints']} " +
          f"{_opts['modeOpts']}\n"
      )
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

  # For single submission file
  elif _opts['mode'] == "getDiagProc": # TODO
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w")
    writePreamble(_f)
    _f.write(
      f"python3 {swd__}/scripts/getDiagProc.py " +
      f"--inputWSDir {_opts['inputWSDir']} " +
      f"--ext {_opts['ext']} " +
      f"{_opts['modeOpts']}\n"
    )
    _f.close()
    os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeSubFilesMgg(_opts):
  if _opts['batch'] == "condor":
    writeCondorSubFilesMgg(_opts)
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    writeSGESubFilesMgg(_opts)

def writeSubFilesMjj(_opts):
  if _opts['batch'] == "condor":
    writeCondorSubFilesMjj(_opts)
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    writeSGESubFilesMjj(_opts)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeSubFiles(_opts):
  # Make directory to store sub files
  if not os.path.isdir("%s/outdir_%s"%(swd__,_opts['ext'])): os.system("mkdir %s/outdir_%s"%(swd__,_opts['ext']))
  if not os.path.isdir("%s/outdir_%s/%s"%(swd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s"%(swd__,_opts['ext'],_opts['mode']))
  if not os.path.isdir("%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode']))

  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  # Remove current job files
  if len(glob.glob("%s/*"%_jobdir)): os.system("rm %s/*"%_jobdir)
  
  # Mgg/Mjj logic
  if _opts['fitType'] == "mgg" or _opts['fitType'] == "2D":
    writeSubFilesMgg(_opts)
  if _opts['fitType'] == "mjj" or _opts['fitType'] == "2D":
    writeSubFilesMjj(_opts)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for submitting files to batch system
def submitFilesMgg(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])
    if os.environ['PWD'].startswith("/eos"):
      cmdLine = "cd %s; condor_submit -spool %s.sub; cd %s"%(_jobdir,_executable,swd__)
    else:
      cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,swd__)
    run(cmdLine)
    print("  --> Finished submitting files")

  # SGE
  elif _opts['batch'] in ['IC','SGE']:
    _executable = "sub_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])

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
    elif(_opts['mode'] == "getDiagProc"):
      _subfile = "%s/%s"%(_jobdir,_executable)
      cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
      run(cmdLine)
    print("  --> Finished submitting files")
  
  # Running locally
  elif _opts['batch'] == 'local':
    _executable = "sub_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])
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
    elif(_opts['mode'] == "getDiagProc"):
      _subfile = "%s/%s"%(_jobdir,_executable)
      cmdLine = "bash %s.sh"%_subfile
      run(cmdLine)
    print("  --> Finished running files")


def submitFilesMjj(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(swd__,_opts['ext'],_opts['mode'])
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])
    if os.environ['PWD'].startswith("/eos"):
      cmdLine = "cd %s; condor_submit -spool %s.sub; cd %s"%(_jobdir,_executable,swd__)
    else:
      cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,swd__)
    run(cmdLine)
    print("  --> Finished submitting files")

  # SGE
  elif _opts['batch'] in ['IC','SGE']:
    _executable = "sub_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])

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
    elif(_opts['mode'] == "getDiagProc"):
      _subfile = "%s/%s"%(_jobdir,_executable)
      cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
      run(cmdLine)
    print("  --> Finished submitting files")
  
  # Running locally
  elif _opts['batch'] == 'local':
    _executable = "sub_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])
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
    elif(_opts['mode'] == "getDiagProc"):
      _subfile = "%s/%s"%(_jobdir,_executable)
      cmdLine = "bash %s.sh"%_subfile
      run(cmdLine)
    print("  --> Finished running files")


def submitFiles(_opts):
  if _opts['fitType'] == "mgg" or _opts['fitType'] == "2D":
    submitFilesMgg(_opts)
  if _opts['fitType'] == "mjj" or _opts['fitType'] == "2D":
    submitFilesMjj(_opts)


 
