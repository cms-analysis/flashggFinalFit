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
#sigFitOnly = True
#packageOnly = True
#sigPlotsOnly = True

print 'About to run signal scripts'
print 'isSubmitted = %s, phoSystOnly = %s, sigFitOnly = %s, sigPlotsOnly = %s'%(str(isSubmitted), str(phoSystOnly), str(sigFitOnly), str(sigPlotsOnly))

#setup files 
#ext          = 'reCategorised'
#ext          = 'reCategorised_DCB'
ext          = 'fullStage1combinedBDT'
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
cats  = 'RECO_0J_Tag0,RECO_0J_Tag1,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_GT200,'
cats += 'RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_GT200_Tag0,RECO_GE2J_PTH_GT200_Tag1,RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3VETO_Tag2,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,RECO_VBFTOPO_JET3_Tag2,'
cats += 'RECO_WHLEP,RECO_ZHLEP,RECO_VHLEPLOOSE,RECO_VHMET,RECO_VHHAD,'
cats += 'RECO_TTH_LEP,RECO_TTH_HAD'
print 'with processes: %s'%procs
print 'and categories: %s'%cats

#misc config
lumi          = '35.9'
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
theCommand += './runSignalScripts.sh -i '+fullFileNames+' -p '+procs+' -f '+cats+' --ext '+ext+' --intLumi '+lumi+' --batch '+batch+' --massList '+masses+' --bs '+beamspot
if not useDCB: theCommand += ' --smears '+smears+' --scales '+scales+' --scalesCorr '+scalesCorr+' --scalesGlobal '+scalesGlobal+' --useSSF 1 --useDCB_1G 0'
else: theCommand += ' --smears '+smears+' --scales '+scales+' --scalesCorr '+scalesCorr+' --scalesGlobal '+scalesGlobal+' --useSSF 1 --useDCB_1G 1'
if phoSystOnly: theCommand += ' --calcPhoSystOnly'
elif sigFitOnly: theCommand += ' --sigFitOnly --dontPackage'
elif sigPlotsOnly: theCommand += ' --sigPlotsOnly'
elif packageOnly: theCommand += ' --packageOnly'
if not justPrint: system(theCommand)
else: print '\n\n%s'%theCommand
