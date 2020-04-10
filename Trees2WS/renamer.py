import glob, os, re

vbf = glob.glob("*_VBFHToGG_*_QQ2HQQ_*")
wh = glob.glob("*_WHToGG_*_QQ2HQQ_*")
zh = glob.glob("*_ZHToGG_*_QQ2HQQ_*")
for f in vbf:
  fnew = re.sub("QQ2HQQ","VBF",f)
  os.system("mv %s %s"%(f,fnew))
for f in wh:
  fnew = re.sub("QQ2HQQ","WH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))
for f in zh:
  fnew = re.sub("QQ2HQQ","ZH2HQQ",f)
  os.system("mv %s %s"%(f,fnew))
