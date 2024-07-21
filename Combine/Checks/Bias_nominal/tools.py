import os, sys
# Paths and directory
cmsswbase__ = os.environ['CMSSW_BASE']
cwd__ = os.environ['CMSSW_BASE']+"/src/flashggFinalFit"
wd__ = "%s/Combine/Checks/Bias_nominal"%cwd__


def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)


def writePreamble(_file):
  _file.write("#!/bin/bash\n")
  _file.write("ulimit -s unlimited\n")
  #_file.write("set -e\n")
  _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
  _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
  _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
  _file.write("cd %s\n"%wd__)
  _file.write("cmsenv")
  _file.write("MY.SingularityImage = \"/cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-cat/cmssw-lxplus/cmssw-el7-lxplus:latest/\"")

  _file.write("export PYTHONPATH=$PYTHONPATH:%s/tools:%s/tools\n\n"%(cwd__,wd__))
