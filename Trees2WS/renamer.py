import glob, os, re

from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputDir',dest='inputDir', default="", help='Input path to workspaces')
  return parser.parse_args()
(opt,args) = get_options()

vbf = glob.glob("%s/*_VBFHToGG_*_QQ2HQQ_*"%opt.inputDir)
wh = glob.glob("%s/*_WHToGG_*_QQ2HQQ_*"%opt.inputDir)
zh = glob.glob("%s/*_ZHToGG_*_QQ2HQQ_*"%opt.inputDir)
bbh = glob.glob("%s/*_bbHToGG_*"%opt.inputDir)
th = glob.glob("%s/*_TH*_*"%opt.inputDir)
allf = glob.glob("%s/*"%opt.inputDir)
for f in vbf:
  fnew = re.sub("QQ2HQQ","VBF",f)
  os.system("mv %s %s"%(f,fnew))
for f in wh:
  fnew = re.sub("QQ2HQQ","WH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))
for f in zh:
  fnew = re.sub("QQ2HQQ","ZH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))
for f in bbh:
  fnew = re.sub("M-125","M125",f)
  fnew = re.sub("_amcatnlo","_amcatnlo_pythia8",fnew)
  os.system("mv %s %s"%(f,fnew))
for f in th:
  fnew = re.sub("_TuneCP5","",f)
  os.system("mv %s %s"%(f,fnew))
for f in allf:
  if "-" in f:
    fnew = re.sub("-","_",f)
    os.system("mv %s %s"%(f,fnew))

