import ROOT
import glob

fName = "/vols/cms/jl2117/hgg/ws/Feb20_unblinding/stage1_2_2018/tagsetthree/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLNU_PTV_0_75.root"

cats = "RECO_WH_LEP_LOW_Tag0,RECO_WH_LEP_LOW_Tag1,RECO_WH_LEP_LOW_Tag2".split(",")

nWV, sWV = {}, {}


f = ROOT.TFile( fName )
ws = f.Get("tagsDumper/cms_hgg_13TeV")

for cat in cats:
  nWV[cat] = 0
  sWV[cat] = 0
  d = ws.data("wh_125_13TeV_%s"%cat)
  for i in range(d.numEntries()):
    p = d.get(i)
    w = d.weight()
    dz = p.getRealValue("dZ")
    if abs(dz) > 1.:
      nWV[cat] += 1
      sWV[cat] += w


