#script used to find the proc,cat of jobs that failed in signal fitting
from os import system, walk

ext = 'fullStage1Test'
dirName = 'outdir_%s/sigfit/SignalFitJobs/'%ext

for root, dirs, files in walk(dirName):
  for fileName in files:
    #if not 'fail' in fileName: continue
    #fileName = fileName.replace('.fail','.log')
    if not 'done' in fileName: continue
    fileName = fileName.replace('.done','.log')
    with open(dirName+fileName,'r') as f: theInput = f.read().splitlines()
    proc = ''
    cat  = ''
    rv = False
    wv = False
    for line in theInput:
      if 'Running fits for proc' in line: 
        proc = line.split('proc:')[1].split(' ')[0]
        cat  = line.split('cat:')[1].split(' ')[0]
      if 'too few entries to use for fits in RV' in line:
        rv = True
      if 'too few entries to use for fits in WV' in line:
        wv = True
    print 'proc cat: %s %s \nrv wv: %s %s'%(proc, cat, str(rv), str(wv))
    if not rv and not wv: print 'location is %s \n'%(dirName+fileName)
    else: print ''
