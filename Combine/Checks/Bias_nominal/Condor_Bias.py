import concurrent.futures
from biasUtils import *
import os
from optparse import OptionParser
from submissionTools import writeCondorSub

parser = OptionParser()

parser.add_option("--cat",default='')
parser.add_option("--step",default='NominaToys')

(opts,args) = parser.parse_args()
print('OutputBias'+opts.step+'_Jobs'+opts.cat,'OutputBias_txt/OutputBias'+opts.step+opts.cat+'.txt' )

writeSubFiles('OutputBias'+opts.step+'_Jobs'+opts.cat,'NominalToy_24_06_04/Toys.txt', batch = 'condor')