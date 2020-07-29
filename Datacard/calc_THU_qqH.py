import re
from collections import OrderedDict as od

with open("THU_qqH_relative.txt","r") as f:
  lines = []
  for line in f: lines.append(line)

snames = "".join(lines[0].split(" "))[2:-1].split("|")[:-1]
relativeUnc = {}
for line in lines[1:]:
  b, vals = "".join(line[:-1].split(" ")).split(":")
  vals = vals.split("|")[:-1]
  relativeUnc[int(b)] = {}
  for i in range(len(vals)): relativeUnc[int(b)][snames[i]] = float(vals[i])*0.01

# XS
fine_xs = od()
fine_xs[200] = 470.616
fine_xs[201] = 416.752
fine_xs[202] = 1948.572
fine_xs[203] = 46.574
fine_xs[204] = 341.685
fine_xs[205] = 344.551
fine_xs[206] = 68.774
fine_xs[207] = 244.861
fine_xs[208] = 301.698
fine_xs[209] = 398.061
fine_xs[210] = 164.063
fine_xs[211] = 207.287
fine_xs[212] = 66.900
fine_xs[213] = 190.095
fine_xs[214] = 52.562
fine_xs[215] = 197.090
fine_xs[216] = 39.209
fine_xs[217] = 22.498
fine_xs[218] = 27.417
fine_xs[219] = 18.880
fine_xs[220] = 15.220
fine_xs[221] = 22.996
fine_xs[222] = 14.850
fine_xs[223] = 32.095
fine_xs[224] = 14.967

# Bin definitions
stage1p2_bins = od()
stage1p2_bins['FWDH'] = [200]
stage1p2_bins['0J'] = [201]
stage1p2_bins['1J'] = [202]
stage1p2_bins['GE2J_MJJ_0_60'] = [203,214]
stage1p2_bins['GE2J_MJJ_60_120'] = [204,215]
stage1p2_bins['GE2J_MJJ_120_350'] = [205,216]
stage1p2_bins['GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = [206]
stage1p2_bins['GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = [217]
stage1p2_bins['GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = [207,208,209]
stage1p2_bins['GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = [218,219,220]
stage1p2_bins['GE2J_MJJ_GT350_PTH_GT200'] = [210,211,212,213,221,222,223,224]

stage1p2_xs = od()
stage1p2_absoluteUnc = od()
stage1p2_relativeUnc = od()
for k, v in stage1p2_bins.iteritems():
  stage1p2_xs[k] = 0
  stage1p2_absoluteUnc[k] = od()
  stage1p2_relativeUnc[k] = od()
  for b in v: stage1p2_xs[k] += fine_xs[b]
  # Unc
  for s in snames: 
    stage1p2_absoluteUnc[k][s] = 0
    for b in v: stage1p2_absoluteUnc[k][s] += fine_xs[b]*relativeUnc[b][s]
    stage1p2_relativeUnc[k][s] = stage1p2_absoluteUnc[k][s]/stage1p2_xs[k]

stage1p2_var = od()
for k, systs in stage1p2_relativeUnc.iteritems():
  stage1p2_var[k] = od()
  for s, ru in systs.iteritems():
    s = re.sub("PTH25","PTHJJ25",s)
    s = re.sub("Mjj","MJJ",s)
    stage1p2_var[k][s] = 1.0+ru

# Write out to json file
with open("thu_qqh_stxs_new.json","w") as f:
  f.write("{\n")
  for k, systs in stage1p2_var.iteritems():
    for proc in ['qqH','WH_had','ZH_had']:
      f.write("    \"%s_%s\":{\n"%(proc,k))
      for s,v in systs.iteritems():
        if s == "JET01": f.write("        \"THU_qqH_%s\":%.4f\n"%(s,v))
        else: f.write("        \"THU_qqH_%s\":%.4f,\n"%(s,v))
      f.write("    },\n")
  f.write("}")

