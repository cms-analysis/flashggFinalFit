#!/usr/bin/env python

from biasUtils import *

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--datacard",default="Datacard.root")
parser.add_option("-w","--workspace",default="w")
parser.add_option("-t","--toys",action="store_true", default=False)
parser.add_option("-n","--nToys",default=1000,type="int")
parser.add_option("-f","--fits",action="store_true", default=False)
parser.add_option("-p","--plots",action="store_true", default=False)
parser.add_option("-e","--expectSignal",default=1.,type="float")
parser.add_option("-m","--mH",default=125.,type="float")
parser.add_option("-c","--combineOptions",default="")
parser.add_option("-s","--seed",default=-1,type="int")
parser.add_option("--dryRun",action="store_true", default=False)
parser.add_option("--poi",default="r")
parser.add_option("--split",default=500,type="int")
parser.add_option("--selectFunction",default=None)
parser.add_option("--gaussianFit",action="store_true", default=False)
(opts,args) = parser.parse_args()
print
if opts.nToys>opts.split and not opts.nToys%opts.split==0: raise RuntimeError('The number of toys %g needs to be smaller than or divisible by the split number %g'%(opts.nToys, opts.split))

import ROOT as r
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(2211)

ws = r.TFile(opts.datacard).Get(opts.workspace)

pdfs = rooArgSetToList(ws.allPdfs())
multipdfName = None
for pdf in pdfs:
    if pdf.InheritsFrom("RooMultiPdf"):
        if multipdfName is not None: raiseMultiError() 
        multipdfName = pdf.GetName()
        print 'Conduct bias study for multipdf called %s'%multipdfName
multipdf = ws.pdf(multipdfName)
print

varlist = rooArgSetToList(ws.allCats())
indexName = None
for var in varlist:
    if var.GetName().startswith('pdfindex'):
        if indexName is not None: raiseMultiError()
        indexName = var.GetName()
        print 'Found index called %s'%indexName
print

from collections import OrderedDict as od
indexNameMap = od()
for ipdf in range(multipdf.getNumPdfs()):
    if opts.selectFunction is not None:
        if not multipdf.getPdf(ipdf).GetName().count(opts.selectFunction): continue
    indexNameMap[ipdf] = multipdf.getPdf(ipdf).GetName()

if opts.toys:
    if not path.isdir('BiasToysn'): system('mkdir -p BiasToys')
    toyCmdBase = 'combine -m %.4f -d %s -M GenerateOnly --expectSignal %.4f -s %g --saveToys %s '%(opts.mH, opts.datacard, opts.expectSignal, opts.seed, opts.combineOptions)
    for ipdf,pdfName in indexNameMap.iteritems():
        name = shortName(pdfName)
        if opts.nToys > opts.split:
            for isplit in range(opts.nToys//opts.split):
                toyCmd = toyCmdBase + ' -t %g -n _%s_split%g --setParameters %s=%g --freezeParameters %s'%(opts.split, name, isplit, indexName, ipdf, indexName)
                run(toyCmd, dry=opts.dryRun)
                system('mv higgsCombine_%s* %s'%(name, toyName(name,split=isplit)))
        else: 
            toyCmd = toyCmdBase + ' -t %g -n _%s --setParameters %s=%g --freezeParameters %s'%(opts.nToys, name, indexName, ipdf, indexName)
            run(toyCmd, dry=opts.dryRun)
            system('mv higgsCombine_%s* %s'%(name, toyName(name)))
print

if opts.fits:
    if not path.isdir('BiasFits'): system('mkdir -p BiasFits')
    fitCmdBase = 'combine -m %.4f -d %s -M MultiDimFit -P %s --algo singles %s '%(opts.mH, opts.datacard, opts.poi, opts.combineOptions)
    for ipdf,pdfName in indexNameMap.iteritems():
        name = shortName(pdfName)
        if opts.nToys > opts.split:
            for isplit in range(opts.nToys//opts.split):
                fitCmd = fitCmdBase + ' -t %g -n _%s_split%g --toysFile=%s'%(opts.split, name, isplit, toyName(name,split=isplit))
                run(fitCmd, dry=opts.dryRun)
                system('mv higgsCombine_%s* %s'%(name, fitName(name,split=isplit)))
            run('hadd %s BiasFits/*%s*split*.root'%(fitName(name),name), dry=opts.dryRun)
        else:
            fitCmd = fitCmdBase + ' -t %g -n _%s --toysFile=%s'%(opts.nToys, name, toyName(name))
            run(fitCmd, dry=opts.dryRun)
            system('mv higgsCombine_%s* %s'%(name, fitName(name)))

if opts.plots:
    if not path.isdir('BiasPlots'): system('mkdir -p BiasPlots')
    for ipdf,pdfName in indexNameMap.iteritems():
        name = shortName(pdfName)
        tfile = r.TFile(fitName(name))
        tree = tfile.Get('limit')
        pullHist = r.TH1F('pullsForTruth_%s'%name, 'Pull distribution using the envelope to fit %s'%name, 80, -4., 4.)
        pullHist.GetXaxis().SetTitle('Pull')
        pullHist.GetYaxis().SetTitle('Entries')
        for itoy in range(opts.nToys):
            tree.GetEntry(3*itoy)
            if not getattr(tree,'quantileExpected')==-1: 
                raiseFailError(itoy,True) 
                continue
            bf = getattr(tree, 'r')
            tree.GetEntry(3*itoy+1)
            if not abs(getattr(tree,'quantileExpected')--0.32)<0.001: 
                raiseFailError(itoy,True) 
                continue
            lo = getattr(tree, 'r')
            tree.GetEntry(3*itoy+2)
            if not abs(getattr(tree,'quantileExpected')-0.32)<0.001: 
                raiseFailError(itoy,True) 
                continue
            hi = getattr(tree, 'r')
            diff = bf - opts.expectSignal
            unc = 0.5 * (hi-lo)
            if unc > 0.: 
                pullHist.Fill(diff/unc)
        canv = r.TCanvas()
        pullHist.Draw()
        if opts.gaussianFit:
           r.gStyle.SetOptFit(111)
           pullHist.Fit('gaus')
        canv.SaveAs('%s.pdf'%plotName(name))
        canv.SaveAs('%s.png'%plotName(name))
