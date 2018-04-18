#commands to send to the monolithic runFinalFits.sh script
from os import system, walk

justPrint=False
#justPrint=True
unblind = False
#unblind = True
fTestOnly = False
#fTestOnly = True
#bkgPlotsOnly = False
bkgPlotsOnly = True
print 'About to run background scripts'
print 'fTestOnly = %s, bkgPlotsOnly = %s'%(str(fTestOnly), str(bkgPlotsOnly))

#setup files 
ext          = 'fullStage1Test'
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

#masses to be considered
masses        = '120,123,124,125,126,127,130'
massLow       = '120'
massHigh      = '130'
print 'masses %s'%masses

#input files
dataFile      = baseFilePath+'allData.root'
sigFile       = '/vols/build/cms/es811/FreshStart/STXSstage1/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_%s/CMS-HGG_sigfit_%s.root'%(ext,ext)

theCommand = ''
theCommand += './runBackgroundScripts.sh -i '+dataFile+' -p '+procs+' -f '+cats+' --ext '+ext+' --intLumi '+lumi+' --batch '+batch+' --sigFile '+sigFile+' --isData '
if   fTestOnly:    theCommand += '--fTestOnly '
elif bkgPlotsOnly: theCommand += '--bkgPlotsOnly '
if unblind and not fTestOnly: theCommand += '--unblind '
if justPrint: print theCommand
else: system(theCommand)
