#!/usr/bin/env python

# CHECK

#commands to send to the monolithic runFinalFits.sh script
from os import system, walk

justPrint=False
isSubmitted = False
phoSystOnly = False
useDCB = False
sigFitOnly = False
packageOnly = False
sigPlotsOnly = False

#justPrint=True
#isSubmitted = True
#phoSystOnly = True
#useDCB = True
sigFitOnly = True
#packageOnly = True
#sigPlotsOnly = True

print 'About to run signal scripts'
print 'isSubmitted = %s, phoSystOnly = %s, sigFitOnly = %s, sigPlotsOnly = %s'%(str(isSubmitted), str(phoSystOnly), str(sigFitOnly), str(sigPlotsOnly))

#setup files 
ext = 'ReweighAndNewggHweights'
print 'ext = %s'%ext

baseFilePath  = '/vols/cms/es811/FinalFits/ws_%s/'%ext
fileNames     = []
for root,dirs,files in walk(baseFilePath):
  for fileName in files: 
    if not fileName.startswith('output_'): continue
    if not fileName.endswith('.root'):     continue
    fileNames.append(fileName)
fullFileNames = '' 
for fileName in fileNames: fullFileNames += baseFilePath+fileName+','
fullFileNames = fullFileNames[:-1]
#print 'fileNames = %s'%fullFileNames

#define processes and categories
procs         = ''
for fileName in fileNames: 
  if 'M125' not in fileName: continue
  procs += fileName.split('pythia8_')[1].split('.root')[0]
  procs += ','
procs = procs[:-1]
cats  = 'UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,VHHadronicTag,VHMetTag'
#cats  = 'UntaggedTag_0,VBFTag_0'
#cats  = 'RECO_0J_Tag0,RECO_0J_Tag1,RECO_0J_Tag2,'
#cats += 'RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_GT200,'
#cats += 'RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_GT200_Tag0,RECO_GE2J_PTH_GT200_Tag1,'
#cats += 'RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,RECO_VBFTOPO_REST,RECO_VBFTOPO_BSM'
print 'with processes: %s'%procs
print 'and categories: %s'%cats

#FIXME temp for packaging...
#procs = 'GG2H_1J_PTH_0_60,GG2H_GE2J_PTH_0_60,QQ2HLNU_PTV_150_250_0J,WH2HQQ_VBFTOPO_JET3,WH2HQQ_VH2JET,ZH2HQQ_VH2JET,GG2H_1J_PTH_60_120,VBF_VBFTOPO_JET3,QQ2HLL_PTV_150_250_0J,QQ2HLL_PTV_150_250_GE1J,GG2H_1J_PTH_GT200,testTHW,QQ2HLNU_PTV_150_250_GE1J,testTHQ,TTH,VBF_PTJET1_GT200,QQ2HLL_PTV_GT250,GG2H_0J,GG2H_GE2J_PTH_60_120,GG2H_GE2J_PTH_GT200,WH2HQQ_REST,WH2HQQ_VBFTOPO_JET3VETO,GGZH,VBF_REST,ZH2HQQ_REST,ZH2HQQ_VBFTOPO_JET3,GG2H_VBFTOPO_JET3,GG2H_VBFTOPO_JET3VETO,VBF_VBFTOPO_JET3VETO,VBF_VH2JET,WH2HQQ_PTJET1_GT200,ZH2HQQ_PTJET1_GT200,ZH2HQQ_VBFTOPO_JET3VETO,QQ2HLNU_PTV_0_150,QQ2HLL_PTV_0_150,GG2H_1J_PTH_120_200,GG2H_GE2J_PTH_120_200,QQ2HLNU_PTV_GT250 -f RECO_0J_Tag0,RECO_0J_Tag1,RECO_0J_Tag2,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_GT200,RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_GT200_Tag0,RECO_GE2J_PTH_GT200_Tag1,RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,RECO_VBFTOPO_REST,RECO_VBFTOPO_BSM,testBBH'

#misc config
analysis      = 'hig-16-040' # Specifies the replacement dataset mapping to use: defined in Signal/python/replacementMap.py
lumi          = '35.9'
if '2017' in ext: lumi = '41.5'
batch         = 'IC'
queue         = 'hep.q'
beamspot      = '3.4'
nBins         = '320'
print 'lumi %s'%lumi
print 'batch %s'%batch
print 'queue %s'%queue
print 'beamspot %s'%beamspot
print 'nBins %s'%nBins

#photon shape systematics
scales        = 'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB'
scalesCorr    = 'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB'
scalesGlobal  = 'NonLinearity:UntaggedTag_0:2,Geant4'
smears        = 'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho'
#print 'scales %s'%scales
#print 'scalesCorr %s'%scalesCorr
#print 'scalesGlobal %s'%scalesGlobal
#print 'smears %s'%smears

#masses to be considered
#masses        = '120,123,124,125,126,127,130'
masses        = '120,125,130'
massLow       = '120'
massHigh      = '130'
print 'masses %s'%masses

theCommand = ''
if isSubmitted:
  theCommand += ('cd /vols/build/cms/es811/FreshStart/STXSstage1/CMSSW_7_4_7/src/flashggFinalFit/Signal\n')
  theCommand += ('eval `scramv1 runtime -sh`\n')
theCommand += './runSignalScripts.sh -i '+fullFileNames+' -p '+procs+' -f '+cats+' --ext '+ext+' --intLumi '+lumi+' --batch '+batch+' --massList '+masses+' --bs '+beamspot+' --analysis '+analysis
if not useDCB: theCommand += ' --smears '+smears+' --scales '+scales+' --scalesCorr '+scalesCorr+' --scalesGlobal '+scalesGlobal+' --useSSF 1 --useDCB_1G 0'
else: theCommand += ' --smears '+smears+' --scales '+scales+' --scalesCorr '+scalesCorr+' --scalesGlobal '+scalesGlobal+' --useSSF 1 --useDCB_1G 1'
if phoSystOnly: theCommand += ' --calcPhoSystOnly'
elif sigFitOnly: theCommand += ' --sigFitOnly --dontPackage'
elif sigPlotsOnly: theCommand += ' --sigPlotsOnly'
elif packageOnly: theCommand += ' --packageOnly'
if not justPrint: system(theCommand)
else: print '\n\n%s'%theCommand
