#!/usr/bin/env python

def rooArgSetToList(argset): ## taken from Andrea Marini's great repo here: https://github.com/amarini/rfwsutils/blob/master/wsutils.py#L300-L313
    """creates a python list with the contents of argset (which should be a RooArgSet)"""
    it = argset.createIterator()

    retval = []
    while True:
        obj = it.Next()

        if obj == None:
            break

        retval.append(obj)

    return retval

def raiseMultiError(lax=False):
    raise RuntimeError('Found more than one multipdf here - please create a workspace with just one for these bias studies. You can use "combineCards.py Datacard.txt --ic cat_name" for this)')

def raiseFailError(itoy, lax=False):
    text = 'some fits have failed, wrong quantile for toy number %g'%itoy
    if not lax: raise RuntimeError('ERROR %s'%text)
    else: print 'WARNING %s'%text

def shortName(name):
    return name.split('_')[-1]

def toyName(name, split=None):
    retval = 'BiasToys/biasStudy_%s_toys.root'%name
    if split is not None: 
        split = int(split)
        retval = retval.replace(name,'%s_split%g'%(name,split))
    return retval

def fitName(name, split=None):
    retval = 'BiasFits/biasStudy_%s_fits.root'%name
    if split is not None: 
        split = int(split)
        retval = retval.replace(name,'%s_split%g'%(name,split))
    return retval

def plotName(name):
    return 'BiasPlots/biasStudy_%s_pulls'%name

def run(cmd, dry=False):
   print cmd
   if not dry: system(cmd)
