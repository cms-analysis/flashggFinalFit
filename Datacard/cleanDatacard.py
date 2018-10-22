#!/usr/bin/env python

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--datacard", help="Datacard to be cleaned")
parser.add_option("-o","--outfilename",default=None,help="Output datacard file")
parser.add_option("--removeDoubleSided",default=False,action="store_true",help="Remove any nuisances which are listed as antisymmetric but both values point the same way")
(opts,args)=parser.parse_args()

if not opts.outfilename: 
  opts.outfilename = opts.datacard.replace('.txt','_cleaned.txt')

with open(opts.outfilename,'w') as outFile:
  with open(opts.datacard) as inFile:
    for line in inFile.readlines():
      vals = line.split()
      if len(vals) < 2 or vals[1]!='lnN': 
        outFile.write('%s'%line)
        continue
      line = line.split('lnN')[0] + 'lnN   '
      for effect in vals[2:]:
        vals = effect.split('/')
        if len(vals) == 1:
          if vals[0] == '-':
            line += '- '
          else:
            val = float(vals[0])
            if val <= 0.2 or val >=5.:
              line += '- '
            else:
              line += '%1.3f '%val
        elif len(vals) == 2:
          valLo = float(vals[0])
          valHi = float(vals[1])
          if valLo <= 0.2 or valLo >=5.:
            valLo = 1
          if valHi <= 0.2 or valHi >=5.:
            valHi = 1
          if opts.removeDoubleSided and valHi >= 1 and valLo >= 1:
            line += '%1.3f '%(0.5*(valHi+valLo))
          elif opts.removeDoubleSided and valHi < 1 and valLo <= 1:
            line += '%1.3f '%(0.5*(valHi+valLo))
          else:
            line += '%1.3f/%1.3f '%(valLo,valHi)
        else:
          exit('should only be of length one or two!!!')
      outFile.write('%s\n'%line)
