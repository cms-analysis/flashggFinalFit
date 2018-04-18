#commands to send to the monolithic runFinalFits.sh script
from os import system, walk

justPrint = False
datacardOnly = False
combineOnly = False
combinePlotsOnly = False
effAccOnly = False
yieldsOnly = False

#justPrint = True
#datacardOnly = True
combineOnly = True
#combinePlotsOnly = True
#effAccOnly = True
#yieldsOnly = True

print 'About to run combine scripts'
print 'datacardOnly = %s, combineOnly = %s, combinePlotsOnly = %s, effAccOnly = %s, yieldsOnly = %s'%(str(datacardOnly), str(combineOnly), str(combinePlotsOnly), str(effAccOnly), str(yieldsOnly) )

#setup files 
ext          = 'fullStage1Test'
#ext          = 'fullStage1Test_DCB'
print 'ext = %s'%ext
#baseFilePath  = '/vols/cms/es811/FinalFits/ws_%s/'%ext
baseFilePath  = '/vols/cms/es811/FinalFits/ws_fullStage1Test/'
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
for fileName in fileNames: 
  if 'M125' in fileName: files125 += baseFilePath+fileName+','
files125 = files125[:-1]
#print 'fileNames = %s'%fullFileNames

#define processes and categories
procs         = ''
for fileName in fileNames: 
  if 'M125' not in fileName: continue
  procs += fileName.split('pythia8_')[1].split('.root')[0]
  procs += ','
procs = procs[:-1]
#cats          = 'RECO_0J,RECO_1J_PTH_0_60,RECO_1J_PTH_60_120,RECO_1J_PTH_120_200,RECO_1J_PTH_GT200,RECO_GE2J_PTH_0_60,RECO_GE2J_PTH_60_120,RECO_GE2J_PTH_120_200,RECO_GE2J_PTH_GT200,RECO_VBFTOPO_JET3VETO,RECO_VBFTOPO_JET3,RECO_VH2JET,RECO_0LEP_PTV_0_150,RECO_0LEP_PTV_150_250_0J,RECO_0LEP_PTV_150_250_GE1J,RECO_0LEP_PTV_GT250,RECO_1LEP_PTV_0_150,RECO_1LEP_PTV_150_250_0J,RECO_1LEP_PTV_150_250_GE1J,RECO_1LEP_PTV_GT250,RECO_2LEP_PTV_0_150,RECO_2LEP_PTV_150_250_0J,RECO_2LEP_PTV_150_250_GE1J,RECO_2LEP_PTV_GT250,RECO_TTH_LEP,RECO_TTH_HAD'
cats          = 'RECO_0J,RECO_1J_PTH_0_60,RECO_1J_PTH_60_120,RECO_1J_PTH_120_200,RECO_1J_PTH_GT200,RECO_GE2J_PTH_0_60,RECO_GE2J_PTH_60_120,RECO_GE2J_PTH_120_200,RECO_GE2J_PTH_GT200,RECO_VBFTOPO_JET3VETO,RECO_VBFTOPO_JET3,RECO_VH2JET,RECO_0LEP_PTV_0_150,RECO_0LEP_PTV_150_250_0J,RECO_0LEP_PTV_150_250_GE1J,RECO_0LEP_PTV_GT250,RECO_1LEP_PTV_0_150,RECO_1LEP_PTV_150_250_0J,RECO_1LEP_PTV_150_250_GE1J,RECO_1LEP_PTV_GT250,RECO_2LEP_PTV_0_150,RECO_TTH_LEP,RECO_TTH_HAD' #zero entry cats removed
print 'with processes: %s'%procs
print 'and categories: %s'%cats

#misc config
lumi          = '35.9'
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

#masses to be considered
masses        = '120,123,124,125,126,127,130'
massLow       = '120'
massHigh      = '130'

#input files
dataFile      = baseFilePath+'allData.root'
sigFile       = '/vols/build/cms/es811/FreshStart/STXSstage1/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_%s/CMS-HGG_sigfit_%s.root'%(ext,ext)

theCommand = './runFinalFitsScripts.sh -i '+files125+' -p '+procs+' -f '+cats+' --ext '+ext+' --intLumi '+lumi+' --batch '+batch+' --dataFile '+dataFile+' --isData '
if   datacardOnly:     theCommand += '--datacardOnly --smears '+smears+' --scales '+scales+' --scalesCorr '+scalesCorr+' --scalesGlobal '+scalesGlobal+' --doStage1'
elif combineOnly:      theCommand += '--combineOnly '
elif combinePlotsOnly: theCommand += '--combinePlotsOnly'
elif effAccOnly:       pass
elif yieldsOnly:       pass
if justPrint: print theCommand
else: system(theCommand)

#./yieldsTableColour.py -w $FILE125 -s Signal/signumbers_${EXT}.txt -u Background/CMS-HGG_multipdf_$EXT.root --factor $INTLUMI -f $CATS --order "Total,GG2H,VBF,TTH,testBBH,testTHQ,testTHW,QQ2HLNU,QQ2HLL,WH2HQQ,ZH2HQQ:Untagged Tag 0,Untagged Tag 1,Untagged Tag 2,Untagged Tag 3,VBF Tag 0,VBF Tag 1,VBF Tag 2,TTH Hadronic Tag,TTH Leptonic Tag,ZH Leptonic Tag,WH Leptonic Tag,VH LeptonicLoose Tag,VH Hadronic Tag,VH Met Tag,Total"
#./makeEffAcc.py $EFFACCFILE Signal/outdir_${EXT}/sigfit/effAccCheck_all.root $INTLUMI
