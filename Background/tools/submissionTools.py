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
  _file.write("cd %s\n"%bwd__)
  _file.write("export PYTHONPATH=$PYTHONPATH:%s/tools:%s/tools\n\n"%(cwd__,bwd__))

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
def writeSubFilesMgg(_opts):
  if _opts['batch'] == 'condor':
    writeCondorSubFilesMgg(_opts)
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    writeSGESubFilesMgg(_opts)

def writeSubFilesMjj(_opts):
  if _opts['batch'] == 'condor':
    writeCondorSubFilesMjj(_opts)
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    writeSGESubFilesMjj(_opts)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeCondorSubFilesMgg(_opts):
  # CONDOR
  _jobdir = "%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])
  _executable = "condor_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])
  _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
  writePreamble(_f)

  # For looping over categories
  if( _opts['mode'] == "fTestParallel" ):
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      co = _opts['catOffset']+cidx
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      # _cmd = "%s/runBackgroundScripts.sh -i %s -p %s -f %s --ext %s --catOffset %g --intLumi %s --year %s --batch %s --queue %s --sigFile %s --isData --fTest"%(bwd__,_opts['dataFile'],_opts['procs'],c,_opts['ext'],co,_opts['lumi'],_opts['year'],_opts['batch'],_opts['queue'],_opts['signalFitWSFile'])
      _cmd = (
          f"{bwd__}/runBackgroundScripts.sh"
          f" -i {_opts['dataFile']}"
          f" -p {_opts['procs']}"
          f" -f {c}"
          f" --ext {_opts['ext']}"
          f" --catOffset {co}"
          f" --intLumi {_opts['lumi']}"
          f" --year {_opts['year']}"
          f" --batch {_opts['batch']}"
          f" --queue {_opts['queue']}"
          f" --sigFile {_opts['signalFitWSFile']}"
          f" --massLow {_opts['mggLow']}"
          f" --massHigh {_opts['mggHigh']}"
          f" --binWidth {_opts['binWidth']}"
          f" --fitType mgg"
          f" --isData --fTest"
        )
      _f.write("  %s\n"%_cmd)
      _f.write("fi\n")
    
  # Close .sh file
  _f.close()
  os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

  # Condor submission file
  _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
  if( _opts['mode'] == "fTestParallel" ):
    writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
  _fsub.close()


def writeCondorSubFilesMjj(_opts):
  # CONDOR
  _jobdir = "%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])
  _executable = "condor_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])
  _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
  writePreamble(_f)

  # For looping over categories
  if( _opts['mode'] == "fTestParallel" ):
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      co = _opts['catOffset']+cidx
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      # _cmd = "%s/runBackgroundScripts.sh -i %s -p %s -f %s --ext %s --catOffset %g --intLumi %s --year %s --batch %s --queue %s --sigFile %s --isData --fTest"%(bwd__,_opts['dataFile'],_opts['procs'],c,_opts['ext'],co,_opts['lumi'],_opts['year'],_opts['batch'],_opts['queue'],_opts['signalFitWSFile'])
      _cmd = (
          f"{bwd__}/runBackgroundScripts.sh"
          f" -i {_opts['dataFile']}"
          f" -p {_opts['procs']}"
          f" -f {c}"
          f" --ext {_opts['ext']}"
          f" --catOffset {co}"
          f" --intLumi {_opts['lumi']}"
          f" --year {_opts['year']}"
          f" --batch {_opts['batch']}"
          f" --queue {_opts['queue']}"
          f" --sigFile {_opts['signalFitWSFile']}"
          f" --massLow {_opts['mjjLow']}"
          f" --massHigh {_opts['mjjHigh']}"
          f" --binWidth {_opts['binWidth']}"
          f" --fitType mjj"
          f" --isData --fTest"
      )
      _f.write("  %s\n"%_cmd)
      _f.write("fi\n")
    
  # Close .sh file
  _f.close()
  os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

  # Condor submission file
  _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
  if( _opts['mode'] == "fTestParallel" ): 
    writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
  _fsub.close()
  pass


def writeSGESubFilesMgg(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])
  _executable = "sub_Mgg_%s_%s"%(_opts['mode'],_opts['ext'])

  # Write details depending on mode

  # For separate submission file per category
  if _opts['mode'] == "fTestParallel":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      co = _opts['catOffset']+cidx
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      # _cmd = "%s/runBackgroundScripts.sh -i %s -p %s -f %s --ext %s --catOffset %g --intLumi %s --year %s --batch %s --queue %s --sigFile %s --isData --fTest"%(bwd__,_opts['dataFile'],_opts['procs'],c,_opts['ext'],co,_opts['lumi'],_opts['year'],_opts['batch'],_opts['queue'],_opts['signalFitWSFile'])
      _cmd = (
          f"{bwd__}/runBackgroundScripts.sh"
          f" -i {_opts['dataFile']}"
          f" -p {_opts['procs']}"
          f" -f {c}"
          f" --ext {_opts['ext']}"
          f" --catOffset {co}"
          f" --intLumi {_opts['lumi']}"
          f" --year {_opts['year']}"
          f" --batch {_opts['batch']}"
          f" --queue {_opts['queue']}"
          f" --sigFile {_opts['signalFitWSFile']}"
          f" --massLow {_opts['mggLow']}"
          f" --massHigh {_opts['mggHigh']}"
          f" --binWidth {_opts['binWidth']}"
          f" --fitType mgg"
          f" --isData --fTest"
      )
      _f.write("%s\n"%_cmd)
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))


def writeSGESubFilesMjj(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])
  _executable = "sub_Mjj_%s_%s"%(_opts['mode'],_opts['ext'])

  # Write details depending on mode

  # For separate submission file per category
  if _opts['mode'] == "fTestParallel":
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      co = _opts['catOffset']+cidx
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      # _cmd = "%s/runBackgroundScripts.sh -i %s -p %s -f %s --ext %s --catOffset %g --intLumi %s --year %s --batch %s --queue %s --sigFile %s --isData --fTest"%(bwd__,_opts['dataFile'],_opts['procs'],c,_opts['ext'],co,_opts['lumi'],_opts['year'],_opts['batch'],_opts['queue'],_opts['signalFitWSFile'])
      _cmd = (
          f"{bwd__}/runBackgroundScripts.sh"
          f" -i {_opts['dataFile']}"
          f" -p {_opts['procs']}"
          f" -f {c}"
          f" --ext {_opts['ext']}"
          f" --catOffset {co}"
          f" --intLumi {_opts['lumi']}"
          f" --year {_opts['year']}"
          f" --batch {_opts['batch']}"
          f" --queue {_opts['queue']}"
          f" --sigFile {_opts['signalFitWSFile']}"
          f" --massLow {_opts['mjjLow']}"
          f" --massHigh {_opts['mjjHigh']}"
          f" --binWidth {_opts['binWidth']}"
          f" --fitType mjj"
          f" --isData --fTest"
      )
      _f.write("%s\n"%_cmd)
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeSubFiles(_opts):
  # Make directory to store sub files
  if not os.path.isdir("%s/outdir_%s"%(bwd__,_opts['ext'])): os.system("mkdir %s/outdir_%s"%(bwd__,_opts['ext']))
  if not os.path.isdir("%s/outdir_%s/%s"%(bwd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s"%(bwd__,_opts['ext'],_opts['mode']))
  if not os.path.isdir("%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode']))

  _jobdir = "%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])
  # Remove current job files
  if len(glob.glob("%s/*"%_jobdir)): os.system("rm %s/*"%_jobdir)
  
  # Mgg/Mjj logic
  if _opts['fitType'] == "mgg" or _opts['fitType'] == "2D":
    writeSubFilesMgg(_opts)
  if _opts['fitType'] == "mjj" or _opts['fitType'] == "2D":
    writeSubFilesMjj(_opts)
         

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for submitting files to batch system
def submitFiles(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(bwd__,_opts['ext'],_opts['mode'])
  _observable = "Mgg" if _opts['fitType'] == "mgg" else "Mjj" # Mgg or Mjj
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_%s_%s_%s"%(_observable, _opts['mode'],_opts['ext'])
    if os.environ['PWD'].startswith("/eos"):
      cmdLine = "cd %s; condor_submit -spool %s.sub; cd %s"%(_jobdir,_executable,bwd__)
    else:
      cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,bwd__)
    run(cmdLine)
    print("  --> Finished submitting files")

  # SGE
  elif _opts['batch'] in ['IC','SGE']:
    _executable = "sub_%s_%s_%s"%(_observable, _opts['mode'],_opts['ext'])

    # Extract job opts
    jobOptsStr = _opts['jobOpts']

    # Separate submission per category  
    if( _opts['mode'] == "fTestParallel" ):
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _subfile = "%s/%s_%s"%(_jobdir,_executable,c)
        cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
        run(cmdLine)
    print("  --> Finished submitting files")
  
  # Running locally
  elif _opts['batch'] == 'local':
    _executable = "sub_%s_%s_%s"%(_observable, _opts['mode'],_opts['ext'])

    # Separate submission per category  
    if( _opts['mode'] == "fTestParallel" ):
      for cidx in range(_opts['nCats']):
        c = _opts['cats'].split(",")[cidx]
        _subfile = "%s/%s_%s"%(_jobdir,_executable,c)
        cmdLine = "bash %s.sh"%_subfile
        run(cmdLine)
    print("  --> Finished running files")

 
