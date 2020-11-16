#!/usr/bin/env python

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--datacard", help="Datacard to be cleaned")
parser.add_option("-o","--outfilename",default=None,help="Output datacard file")
parser.add_option("-f","--factor",default=5.,help="Factor beyond which uncertainty is considered incorrect and is removed")
parser.add_option("--removeDoubleSided",default=False,action="store_true",help="Remove any nuisances which are listed as antisymmetric but both values point the same way")
parser.add_option("--removeNonDiagonal",default=False,action="store_true",help="Remove any nuisances which are affect processes unimportant in that category")
#parser.add_option("--addYear",default=True,action="store_true",help="Add the year to names to facilitate combination")
parser.add_option("--verbose",default=False,action="store_true",help="Spit out all the cleaning being done")
(opts,args)=parser.parse_args()

if not opts.outfilename: 
  opts.outfilename = opts.datacard.replace('.txt','_cleaned.txt')

opts.factor = float(opts.factor)
factorLo = 1./opts.factor
factorHi = opts.factor

procs = []
cats  = []

def isDiag( proc, cat):
  if 'ggH_hgg' in proc:
    return 'J_PTH' in cat
  elif 'qqH_hgg' in proc:
    return 'RECO_VBFTOPO' in cat
  elif 'ttH_hgg' in proc:
    return 'TTH' in cat
  elif 'WH_had_hgg' in proc or 'ZH_had_hgg' in proc:
    return 'RECO_VHHAD' in cat
  elif 'WH_lep_hgg' in proc or 'ZH_lep_hgg' in proc:
    return 'LEP' in cat
  else: return False

with open(opts.outfilename,'w') as outFile:
  with open(opts.datacard) as inFile:
    for line in inFile.readlines():
      vals = line.split()
      if len(vals) < 2:
        outFile.write('%s'%line)
        continue
      if vals[0] == 'process':
        procs = vals[1:]
        outFile.write('%s'%line)
        continue
      if vals[0] == 'bin':
        cats  = vals[1:]
        outFile.write('%s'%line)
        continue
      if vals[1]!='lnN': 
        #if not line.count('hggpdfsmrel_13TeV_2016_'): line = line.replace('hggpdfsmrel_13TeV_','hggpdfsmrel_13TeV_2016_')
        #if not line.count('13TeV_2016_bkgshape'): line = line.replace('13TeV_bkgshape','13TeV_2016_bkgshape')
        #if line.count('pdfindex') and not line.count('_13TeV_2016'): line = line.replace('_13TeV','_13TeV_2016')
        outFile.write('%s'%line)
        continue
      print
      print 'Processing line %s'%vals[0]
      line = line.split('lnN')[0] + 'lnN   '
      for i,effect in enumerate(vals[2:]):
        proc = procs[i]
        cat =  cats[i]
        #print 'proc = %s'%proc
        #print 'cat  = %s'%cat
        if opts.removeNonDiagonal and not isDiag(proc,cat):
          line += '- '
          continue
        vals = effect.split('/')
        if len(vals) == 1:
          if vals[0] == '-':
            line += '- '
          else:
            val = float(vals[0])
            if val < factorLo or val > factorHi:
              line += '- '
              if opts.verbose:
                print 'Symmetric: replacing value of %1.3f with -'%val
            else:
              line += '%1.3f '%val
        elif len(vals) == 2:
          valLo = float(vals[0])
          valHi = float(vals[1])
          if valLo < factorLo or valLo > factorHi:
            if opts.verbose:
              print 'Asymmetric: replacing low value of %1.3f with 1'%valLo
            valLo = 1
          if valHi <= factorLo or valHi > factorHi:
            if opts.verbose:
              print 'Asymmetric: replacing high value of %1.3f with 1'%valHi
            valHi = 1
          if opts.removeDoubleSided and valHi > 1.000001 and valLo > 1.000001:
            #line += '%1.3f '%(0.5*(valHi+valLo))
            line += '%1.3f '%(max(valHi,valLo))
            if opts.verbose:
              #print 'DoubleSided: replacing %1.3f/%1.3f with %1.3f'%(valLo, valHi, 0.5*(valHi+valLo))
              print 'DoubleSided: replacing %1.3f/%1.3f with %1.3f'%(valLo, valHi, max(valHi,valLo))
          elif opts.removeDoubleSided and valHi < 0.999999 and valLo < 0.999999:
            #line += '%1.3f '%(0.5*(valHi+valLo))
            line += '%1.3f '%(min(valHi,valLo))
            if opts.verbose:
              #print 'DoubleSided: replacing %1.3f/%1.3f with %1.3f'%(valLo, valHi, 0.5*(valHi+valLo))
              print 'DoubleSided: replacing %1.3f/%1.3f with %1.3f'%(valLo, valHi, min(valHi,valLo))
          else:
            line += '%1.3f/%1.3f '%(valLo,valHi)
        else:
          exit('should only be of length one or two!!!')
      outFile.write('%s\n'%line)
