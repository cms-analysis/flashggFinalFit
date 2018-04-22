fileName = 'potentialNegPdfs_reCategorised.txt'
#fileName = 'potentialNegPdfs_reCategorised_DCB.txt'
with open(fileName, 'r') as f:
  theInput = f.read().splitlines()

issueCombs = []
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
    errorState = True

for issue in issueCombs: print '%s %s %s'%(issue[0], issue[1], issue[2])
