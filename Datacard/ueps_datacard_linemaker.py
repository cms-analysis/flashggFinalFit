from ROOT import *
outFile = open('/vols/build/cms/es811/FreshStart/Pass3/CMSSW_7_4_7/src/flashggFinalFit/Datacard/ueps_lines.dat','w')

files = {'UE':['/vols/cms/es811/FinalFits/ws_900_ueps/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_CUETP8M1Down_GG2H.root','/vols/cms/es811/FinalFits/ws_900_ueps/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_CUETP8M1Up_GG2H.root','/vols/cms/es811/FinalFits/ws_900_ueps/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8_CUETP8M1Down_VBF.root','/vols/cms/es811/FinalFits/ws_900_ueps/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8_CUETP8M1Up_VBF.root'],'PS':['/vols/cms/es811/FinalFits/ws_900_ueps/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_DownPS_GG2H.root','/vols/cms/es811/FinalFits/ws_900_ueps/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_UpPS_GG2H.root','/vols/cms/es811/FinalFits/ws_900_ueps/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8_DownPS_VBF.root','/vols/cms/es811/FinalFits/ws_900_ueps/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8_UpPS_VBF.root']}

uncertainties = ['UE','PS']

procs = ['GG2H','VBF','TTH','QQ2HLL','QQ2HLNU','WH2HQQ','ZH2HQQ','bkg_mass']
procMap = {'GG2H':'ggh','VBF':'vbf','TTH':'tth','QQ2HLNU':'wh','QQ2HLL':'zh','WH2HQQ':'wh','ZH2HQQ':'zh','bkg_mass':'bkg_mass'}

tags = ['UntaggedTag_0',
'UntaggedTag_1',
'UntaggedTag_2',
'UntaggedTag_3',
'VBFTag_0',
'VBFTag_1',
'VBFTag_2',
'TTHLeptonicTag',
'TTHHadronicTag',
'ZHLeptonicTag',
'WHLeptonicTag',
'VHLeptonicLooseTag',
'VHHadronicTag',
'VHMetTag'
]

lines = {}

for uncertainty in uncertainties:
  lines[uncertainty] = ''
  allValues = {}
  for proc in procs:
    procValues = {}
    for filename in files[uncertainty]:
      if proc in filename and 'Up' in filename: 
        wsUp = (TFile(filename)).Get("tagsDumper/cms_hgg_13TeV")
        continue
      elif proc in filename and 'Down' in filename: 
        wsDown = (TFile(filename)).Get("tagsDumper/cms_hgg_13TeV")
        continue
      else: continue
    for tag in tags:
      if not ('GG2H' in proc or 'VBF' in proc): 
        continue
      elif not ('Untagged' in tag or 'VBF' in tag): 
        continue
      dataUp = "%s_%sUp_13TeV_%s" % (procMap[proc],uncertainty,tag) 
      dataDown = "%s_%sDown_13TeV_%s" % (procMap[proc],uncertainty,tag) 
      weightUp = wsUp.data(dataUp).sumEntries()
      weightDown = wsDown.data(dataDown).sumEntries()
      delta = weightUp - weightDown
      sumBoth = weightUp + weightDown
      value = 1. + (delta / sumBoth)
      procValues[tag] = value
    allValues[proc] = procValues
  for tag in tags:
    for proc in procs:
      if not ('GG2H' in proc or 'VBF' in proc): 
        lines[uncertainty] += '- '
        continue
      elif not ('Untagged' in tag or 'VBF' in tag): 
        lines[uncertainty] += '- '
        continue
      value = (allValues[proc])[tag]
      lines[uncertainty] += '%5.3f ' % value
  uncName = 'CMS_hgg_'+uncertainty
  print '%-35s   lnN   '%(uncName)+lines[uncertainty]
  outFile.write('%-35s   lnN   '%(uncName)+lines[uncertainty]+'\n')
outFile.write('\n')
