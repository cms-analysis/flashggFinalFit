#!/usr/bin/env python
from os import system, path
import ROOT as r
from numpy import log
from stage1helpers import YieldInfo, prettyCat
from collections import namedtuple

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-i','--input',default='numbers.txt')
parser.add_option('-s','--siginput',default='signumbers.txt')
parser.add_option('-w','--workspaces',default='')
parser.add_option('-u','--bkgworkspaces',default='')
parser.add_option('-p','--procs', help='Proceses to consider')
parser.add_option('-c','--cats', help='Categories to consider')
parser.add_option('--intLumi', default=35.9, help='Integrated luminosity')
parser.add_option('--sqrts', default=13, help='Centre of mass energy')
parser.add_option('-v','--verbose', default=0)
(opts,args) = parser.parse_args()

opts.intLumi = float(opts.intLumi)
procs    = opts.procs.split(',')
cats     = opts.cats.split(',')
yi = YieldInfo(procs, cats)

if not (opts.workspaces ==''):
  for ws in opts.workspaces.split(','):
    if 'M125' not in ws: continue
    proc = ws.split('pythia8_')[1].split('.root')[0]
    abbrev = yi.getProcAbbrev(proc)
    print
    print 'running the yields code for process',proc
    print 'ws is ',ws
    system('./Signal/bin/SignalFit -i %s --split %s -f %s --checkYield 1 | grep "RECO_" | grep _125_ | grep -v "pdfWeights" > %s.%s.old'%(ws, proc, opts.cats, opts.input, proc))
    oldFile = open('%s.%s.old'%(opts.input,proc),'r')
    newFile = open('%s.%s.new'%(opts.input,proc),'w')
    for line in oldFile.readlines():
      line = line.replace(abbrev,proc)
      newFile.write(line)
    oldFile.close()
    newFile.close()
  system('rm %s*.old'%(opts.input))
  system('cat %s*.new > %s'%(opts.input,opts.input))
  system('rm %s*.new'%(opts.input))

with open(opts.input) as i:
  for line in i.readlines():
    if 'pdfWeight' in line: continue 
    if 'NOTAG' in line.upper(): continue 
    line     = line.split(',')
    theYield = float(line[1]) * opts.intLumi
    line     = line[0].split('_125_13TeV_')
    proc     = line[0]
    abbrev   = yi.getProcAbbrev(proc)
    stage0   = yi.getProcStage0(proc)
    cat      = line[1]
    yi.addSigYield( (proc,cat), theYield )
    yi.addSigYield( proc, theYield )
    if not proc==abbrev:
      yi.addSigYield( (abbrev,cat), theYield )
      yi.addSigYield( abbrev, theYield )
    if not proc==stage0:
      yi.addSigYield( (stage0,cat), theYield )
      yi.addSigYield( stage0, theYield )
    yi.addSigYield( cat, theYield )
    yi.addSigYield( 'Total', theYield )

with open(opts.siginput) as i:
  for line in i.readlines():
    if not 'TABLE' in line: continue
    if not 'sig_mass' in line: continue
    line     = line.split('sig_mass_m125_')[1]
    line     = line.split('=')
    cat      = line[0]
    effsigma = float(line[2])
    halfmax  = float(line[4])
    yi.setEffSigma( cat, effsigma )
    yi.setFWHM( cat, halfmax )

for iCat,cat in enumerate(cats):
  exec_line = '$CMSSW_BASE/src/flashggFinalFit/Background/bin/makeBkgPlots -b %s -o tmp.root -d tmp -c %d --sqrts 13 --intLumi 2.610000 --massStep 1.000 --nllTolerance 0.050 -L 125 -H 125 --higgsResolution %f --isMultiPdf --useBinnedData --doBands -f %s| grep TABLE > bkg.tmp' % (opts.bkgworkspaces, iCat, yi.getEffSigma(cat), opts.cats)
  print exec_line
  system(exec_line)

  with open('bkg.tmp') as i:
    for line in i.readlines():
      if not 'TABLE' in line: continue
      theYield = float(line.split(',')[3])
      yi.addBkgYield(cat, theYield)
      yi.addBkgYield('Total', theYield)


#now write out the table with at stage0 granularity
print
print 'Stage 0 style yields table'
print
stage0procs  = yi.getStage0list()
stage0dict   = yi.getStage0dict()
nStage0procs = len(stage0procs)
print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
line='\\begin{tabular}{ r | c | c | c  | c |'
line = line + ' c | ' #for total
for proc in stage0procs:
  line = line + ' c | '
line = line[:-2] + '}'
print line
print '\\hline'
#print '\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|c|}{SM 125 GeV Higgs boson expected signal} & Bkg & S/(S+B) \\\\ \\cline{2-%d}'%(nStage0procs+3,nStage0procs+4)
print '\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|c|}{SM 125 GeV Higgs boson expected signal} & Bkg & Signif \\\\ \\cline{2-%d}'%(nStage0procs+3,nStage0procs+4)
line = '  &  '
line = line + 'Total & '
for proc in stage0procs:
  line = line + stage0dict[proc] + ' & '
line = line + '  $\\sigma_{eff} $  & $\\sigma_{HM} $ & (GeV$^{-1}$) & \\\\ '
print line 
print '\\hline'

dataLines = []
pc = '\%'
for cat in cats:
  line = ''
  for proc in stage0procs:
    val = 100. * yi.getSigYield((proc,cat)) / yi.getSigYield(cat)
    if val > 0.05:
      line = line + ' &  ' + str('%.1f %s '%(val,pc))
    else: 
      line = line + ' &  ' + str('$<$0.05 %s '%pc)
  allLine  = ' ' + str('%.1f'%yi.getSigYield(cat))
  niceCat = prettyCat(cat)
  #dataLines.append( niceCat + ' & ' + allLine + ' ' + line + ' & %.2f & %.2f & %.1f & %.2f \\\\'%(yi.getEffSigma(cat), yi.getFWHM(cat), yi.getBkgYield(cat), yi.getPurity(cat)) )
  dataLines.append( niceCat + ' & ' + allLine + ' ' + line + ' & %.2f & %.2f & %.1f & %.2f \\\\'%(yi.getEffSigma(cat), yi.getFWHM(cat), yi.getBkgYield(cat), yi.getAMS(cat)) )

# now do total line
cat = 'Total' 
lineCat = cat +' &   ' 
line=''
for proc in stage0procs:
  val = 100. * yi.getSigYield(proc) / yi.getSigYield(cat)
  if val > 0.05: 
    line = line + ' &  ' + str('%.1f %s '%(val,pc))
  else: 
    line = line + ' &  ' + str('$<$0.05 %s '%pc)

allLine = ' ' + str('%.1f'%yi.getSigYield(cat))
#dataLines.append( lineCat + allLine + ' ' + line + ' & %.2f & %.2f & %.1f & %.2f \\\\'%(yi.getTotEffSigma(), yi.getTotFWHM(), yi.getBkgYield(cat), yi.getTotPurity()) )
dataLines.append( lineCat + allLine + ' ' + line + ' & %.2f & %.2f & %.1f & %.2f \\\\'%(yi.getTotEffSigma(), yi.getTotFWHM(), yi.getBkgYield(cat), yi.getTotAMS()) )

for l in dataLines :
  print l

print '\\hline'
print '\end{tabular}'

print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
print
