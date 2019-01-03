#!/usr/bin/env python

#commands to send to the monolithic runFinalFits.sh script
from os import system, walk

justPrint = False
datacardOnly = False
combineOnly = False
combinePlotsOnly = False
effAccOnly = False
yieldsOnly = False

#justPrint = True
datacardOnly = True
#combineOnly = True
#combinePlotsOnly = True
#effAccOnly = True
#yieldsOnly = True

print 'About to run combine scripts'
print 'datacardOnly = %s, combineOnly = %s, combinePlotsOnly = %s, effAccOnly = %s, yieldsOnly = %s'%(str(datacardOnly), str(combineOnly), str(combinePlotsOnly), str(effAccOnly), str(yieldsOnly) )

#setup files 
ext          = 'fullNewTest2016'
#ext          = 'fullNewTest2017'
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
files125 = ''
filesEffAcc = ''
for fileName in fileNames: 
  proc = fileName.split('pythia8_')[1].split('.root')[0]
  if 'M125' in fileName: 
    files125 += baseFilePath+fileName+','
    if 'GG2H' in proc or 'VBF' in proc: 
      filesEffAcc += baseFilePath+fileName+','
  elif 'M120' in fileName or 'M130' in fileName: 
    if 'GG2H' in proc or 'VBF' in proc: 
      filesEffAcc += baseFilePath+fileName+','
files125 = files125[:-1]
filesEffAcc = filesEffAcc[:-1]
#print 'fileNames = %s'%fullFileNames

#define processes and categories
procs         = ''
for fileName in fileNames: 
  if 'M125' not in fileName: continue
  proc = fileName.split('pythia8_')[1].split('.root')[0]
  procs += proc
  procs += ','
procs = procs[:-1]
cats  = 'RECO_0J_Tag0,RECO_0J_Tag1,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_GT200,'
cats += 'RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_GT200_Tag0,RECO_GE2J_PTH_GT200_Tag1,'
cats += 'RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,RECO_VBFTOPO_REST'
print 'with processes: %s'%procs
print 'and categories: %s'%cats

#misc config
lumi          = '35.9'
if '2017' in ext: lumi = '41.3'
batch         = 'IC'
queue         = 'hep.q'
print 'lumi %s'%lumi
print 'batch %s'%batch
print 'queue %s'%queue

#photon shape systematics
scales        = 'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB'
scalesCorr    = 'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB'
scalesGlobal  = 'NonLinearity:UntaggedTag_0:2,Geant4'
smears        = 'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho'

#input files
dataFile      = baseFilePath+'allData.root'
sigFile       = '$PWD/Signal/outdir_%s/CMS-HGG_sigfit_%s.root'%(ext,ext)

theCommand = './runFinalFitsScripts.sh -i '+files125+' -p '+procs+' -f '+cats+' --ext '+ext+' --intLumi '+lumi+' --batch '+batch+' --dataFile '+dataFile+' --isData '
if   datacardOnly:     theCommand += '--datacardOnly --smears '+smears+' --scales '+scales+' --scalesCorr '+scalesCorr+' --scalesGlobal '+scalesGlobal+' --doStage1'
elif combineOnly:      theCommand += '--combineOnly '
elif combinePlotsOnly: theCommand += '--combinePlotsOnly'
elif effAccOnly:       theCommand = './makeStage1EffAcc.py -i '+filesEffAcc+' -s Signal/outdir_'+ext+'/sigfit/effAccCheck_all.root -p '+procs+' -c '+cats #FIXME this doesn't exist yet!
elif yieldsOnly:       theCommand = './stage1yields.py -w '+files125+' -p '+procs+' -s Signal/signumbers_'+ext+'.txt -u Background/CMS-HGG_multipdf_'+ext+'.root --intLumi '+lumi+' -c '+cats
if justPrint: print theCommand
else: system(theCommand)
