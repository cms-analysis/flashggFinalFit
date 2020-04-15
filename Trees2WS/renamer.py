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
for f in vbf:
  fnew = re.sub("QQ2HQQ","VBF",f)
  os.system("mv %s %s"%(f,fnew))
for f in wh:
  fnew = re.sub("QQ2HQQ","WH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))
for f in zh:
  fnew = re.sub("QQ2HQQ","ZH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))
