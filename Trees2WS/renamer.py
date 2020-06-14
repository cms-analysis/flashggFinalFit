import glob, os, re

from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDir',dest='inputDir', default="", help='Input path to workspaces')
  return parser.parse_args()
(opt,args) = get_options()

v2 = glob.glob("%s/*_v2_*"%opt.inputDir)
for f in v2:
  fnew = re.sub("_v2","",f)
  os.system("mv %s %s"%(f,fnew))

vbf = glob.glob("%s/*_VBFHToGG_*_QQ2HQQ_*"%opt.inputDir)
for f in vbf:
  fnew = re.sub("QQ2HQQ","VBF",f)
  os.system("mv %s %s"%(f,fnew))

wh = glob.glob("%s/*_WHToGG_*_QQ2HQQ_*"%opt.inputDir)
for f in wh:
  fnew = re.sub("QQ2HQQ","WH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))

zh = glob.glob("%s/*_ZHToGG_*_QQ2HQQ_*"%opt.inputDir)
for f in zh:
  fnew = re.sub("QQ2HQQ","ZH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))

bbh = glob.glob("%s/*_bbHToGG_*"%opt.inputDir)
for f in bbh:
  fnew = re.sub("M-125","M125",f)
  fnew = re.sub("_amcatnlo","_amcatnlo_pythia8",fnew)
  os.system("mv %s %s"%(f,fnew))

ggzh = glob.glob("%s/*_ggZH*_*"%opt.inputDir)
for f in ggzh:
  fnew = re.sub("_TuneCP5","",f)
  os.system("mv %s %s"%(f,fnew))

th = glob.glob("%s/*_TH*_*"%opt.inputDir)
for f in th:
  fnew = re.sub("_TuneCP5","",f)
  #fnew = re.sub("_TuneCUETP8M1","",f)
  os.system("mv %s %s"%(f,fnew))

allf = glob.glob("%s/*"%opt.inputDir)
for f in allf:
  if "-" in f:
    fnew = re.sub("-","_",f)
    os.system("mv %s %s"%(f,fnew))

