#various helpers for the stage 1 results scripts
import numpy as np

def prettyCat( cat ):
  cat = cat.replace('RECO','')
  cat = cat.replace('PTH_0_60','Low')
  cat = cat.replace('PTH_60_120','Medium')
  cat = cat.replace('PTH_120_200','High')
  cat = cat.replace('PTH_GT200','BSM')
  cat = cat.replace('GE2J','2J')
  cat = cat.replace('VBFTOPO','VBF')
  cat = cat.replace('JET3VETO','2J-like')
  cat = cat.replace('JET3','3J-like')
  cat = cat.replace('REST','Rest')
  cat = cat.replace('WHLEP','WH Leptonic')
  cat = cat.replace('ZHLEP','ZH Leptonic')
  cat = cat.replace('VHLEPLOOSE','VH Leptonic Loose')
  cat = cat.replace('VHMET','VH MET')
  cat = cat.replace('VHHAD','VH Hadronic')
  cat = cat.replace('TTH_LEP','ttH Leptonic')
  cat = cat.replace('TTH_HAD','ttH Hadronic')
  cat = cat.replace('Tag0','Tag 0')
  cat = cat.replace('Tag1','Tag 1')
  cat = cat.replace('_',' ')
  return cat


class YieldInfo():
  '''Take care of all the different signal shape+yield and background yield for summary table'''
  def __init__(self, procs, cats):
    self.procs     = procs
    self.cats      = cats
    self.sigYields = {}
    self.bkgYields = {}
    self.sigYields['Total'] = 0.
    self.bkgYields['Total'] = 0.
    for cat in cats:
      self.sigYields[cat] = 0.
      self.bkgYields[cat] = 0.
      for proc in procs:
        abbrev = self.getProcAbbrev(proc)
        stage0 = self.getProcStage0(proc)
        self.sigYields[(proc,cat)]   = 0.
        self.sigYields[(abbrev,cat)] = 0.
        self.sigYields[(stage0,cat)] = 0.
    for proc in procs:
      abbrev = self.getProcAbbrev(proc)
      stage0 = self.getProcStage0(proc)
      self.sigYields[proc]   = 0.
      self.sigYields[abbrev] = 0.
      self.sigYields[stage0] = 0.
    self.effSigmas = {}
    self.fwhms     = {}

  def addSigYield(self, key, val):
    self.sigYields[key] += val

  def addBkgYield(self, key, val):
    self.bkgYields[key] += val

  def getSigYield(self, key):
    return self.sigYields[key]

  def getBkgYield(self, key):
    return self.bkgYields[key]

  def setEffSigma(self, key, val):
    self.effSigmas[key] = val

  def setFWHM(self, key, val):
    self.fwhms[key] = val

  def getEffSigma(self, key):
    return self.effSigmas[key]

  def getFWHM(self, key):
    return self.fwhms[key]

  def getPurity(self, cat):
    s = 0.68 * self.getSigYield(cat)
    b = 2. * self.getEffSigma(cat) * self.getBkgYield(cat)
    return s/(s+b)

  def getTotPurity(self):
    s = 0.68 * self.getSigYield('Total')
    b = 2. * self.getTotEffSigma() * self.getBkgYield('Total')
    return s/(s+b)

  def getAMS(self, cat, breg = 3.):
    s = 0.68 * self.getSigYield(cat)
    b = 2. * self.getEffSigma(cat) * self.getBkgYield(cat)
    b += breg
    val = (s + b)*np.log(1. + (s/b))
    val = 2*(val - s)
    val = np.sqrt(val)
    return val

  def getTotAMS(self, breg = 3.):
    s = 0.68 * self.getSigYield('Total')
    b = 2. * self.getTotEffSigma() * self.getBkgYield('Total')
    b += breg
    val = (s + b)*np.log(1. + (s/b))
    val = 2*(val - s)
    val = np.sqrt(val)
    return val

  def getTotEffSigma(self):
    theSum = 0.
    sumW   = 0.
    for cat in self.cats:
      theSum += self.getEffSigma(cat) * self.getSigYield(cat)
      sumW   += self.getSigYield(cat)
    return theSum / sumW

  def getTotFWHM(self):
    theSum = 0.
    sumW   = 0.
    for cat in self.cats:
      theSum += self.getFWHM(cat) * self.getSigYield(cat)
      sumW   += self.getSigYield(cat)
    return theSum / sumW

  def getProcAbbrev(self, theProc):
    if   'ZH2HQQ'  in theProc: return 'zh'
    elif 'QQ2HLL'  in theProc: return 'zh'
    elif 'WH2HQQ'  in theProc: return 'wh'
    elif 'QQ2HLNU' in theProc: return 'wh'
    elif 'TTH'     in theProc: return 'tth'
    elif 'GG2H'    in theProc: return 'ggh'
    elif 'VBF'     in theProc: return 'vbf'
    elif 'BBH'     in theProc: return 'bbh'
    elif 'THQ'     in theProc: return 'th'
    elif 'THW'     in theProc: return 'th'
    else:
      print 'Oh dear, didn not get a prefix for proc %s'%theProc
      raise Exception
  
  def getAbbrevList(self):
    return ['ggh', 'vbf', 'tth', 'wh', 'zh']
  
  def getProcStage0(self, theProc):
    if   'ZH2HQQ'  in theProc: return 'ZH2HQQ'
    elif 'QQ2HLL'  in theProc: return 'QQ2HLL'
    elif 'WH2HQQ'  in theProc: return 'WH2HQQ'
    elif 'QQ2HLNU' in theProc: return 'QQ2HLNU'
    elif 'TTH'     in theProc: return 'TTH'
    elif 'GG2H'    in theProc: return 'GG2H'
    elif 'VBF'     in theProc: return 'VBF'
    elif 'BBH'     in theProc: return 'BBH'
    elif 'THQ'     in theProc: return 'THQ'
    elif 'THW'     in theProc: return 'THW'
    else:
      print 'Oh dear, didn not get a Stage 0 name for proc %s'%theProc
      raise Exception
  
  def getStage0list(self):
    return ['GG2H', 'VBF', 'TTH', 'QQ2HLNU', 'WH2HQQ', 'QQ2HLL', 'ZH2HQQ']

  def getStage0dict(self):
    return {'GG2H':'ggH', 'VBF':'VBF', 'TTH':'ttH', 'QQ2HLNU':'WH lep', 'WH2HQQ':'WH had', 'QQ2HLL':'ZH lep', 'ZH2HQQ':'ZH had'}
