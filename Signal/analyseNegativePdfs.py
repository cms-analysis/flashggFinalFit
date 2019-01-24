from os import system

ext='preappFinal2016'

fileName = 'potentialNegPdfs_%s.txt'%ext
with open(fileName, 'r') as f:
  theInput = f.read().splitlines()

issueCombs = []
issueCats = {}
proc  = ''
cat   = ''
vtx   = ''
errorState = False
for line in theInput:
  thePT = ''
  if ' consider ' in line: 
    errorState = False
    line = line.split(' ')
    proc = line[3]
    cat  = line[4]
    vtx  = line[5]
    continue
  elif 'Print Name' in line: continue
  elif 'error' in line and not errorState:
    issueCombs.append( (proc,cat,vtx) )
    if cat in issueCats: issueCats[cat] += 1
    else: issueCats[cat] = 1
    errorState = True

searchDir = '$PWD/outdir_%s/sigfit/SignalFitJobs'%ext
#searchDir = '/vols/build/cms/es811/FreshStart/STXSstage1/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_%s/sigfit/SignalFitJobs'%ext
for issue in issueCombs: 
  grepCmd = 'grep -rl "proc:%s - cat:%s" %s'%(issue[0], issue[1], searchDir)
  print '%s %s %s'%(issue[0], issue[1], issue[2])
  system(grepCmd)
print

for cat,count in issueCats.iteritems():
  if count > 1: 
    print 'suspect that cat %s is problematic'%cat
    print 'has %g problem processes associated with it'%count
print
