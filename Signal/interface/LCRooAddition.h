 /*****************************************************************************
* Project: RooFit *
* Package: RooFitCore *
*File: $Id: LCRooAddition.h,v 1.3 2007/05/11 09:11:30 verkerke Exp $
* Authors:*
* WV, Wouter Verkerke, UC Santa Barbara, verkerke@slac.stanford.edu *
* DK, David Kirkby,UC Irvine, dkirkby@uci.edu *
* *
* Copyright (c) 2000-2005, Regents of the University of California*
*and Stanford University. All rights reserved.*
* *
* Redistribution and use in source and binary forms,*
* with or without modification, are permitted according to the terms*
* listed in LICENSE (http://roofit.sourceforge.net/license.txt) *
*****************************************************************************/
#ifndef LCROO_ADDITION
#define LCROO_ADDITION

#include "RooAbsReal.h"
#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooListProxy.h"
#include "RooObjCacheManager.h"
#include "../interface/LCRooChi2Var.h"

class RooRealVar;
class RooArgList ;

class LCRooAddition : public RooAbsReal {
  public:

    LCRooAddition() ;
    LCRooAddition(const char* name, const char* title, RooAbsPdf* pdf, std::map<int, RooDataHist*> datasets, RooRealVar* MH, RooRealVar *mgg ) ;
    LCRooAddition(const char *name, const char *title, const RooArgList& sumSet, Bool_t takeOwnerShip=kFALSE) ;
    LCRooAddition(const char *name, const char *title, const RooArgList& sumSet1, const RooArgList& sumSet2, Bool_t takeOwnerShip=kFALSE) ;
    virtual ~LCRooAddition() ;

    LCRooAddition(const LCRooAddition& other, const char* name = 0);
    virtual TObject* clone(const char* newname) const { return new LCRooAddition(*this, newname); }

    virtual Double_t defaultErrorLevel() const ;

    void printMetaArgs(std::ostream& os) const ;

    const RooArgList& list1() const { return _set ; }
    const RooArgList& list() const { return _set ; }

    virtual Bool_t forceAnalyticalInt(const RooAbsArg& /*dep*/) const {
      // Force RooRealIntegral to offer all observables for internal integration
      return kTRUE ;
    }
    Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& numVars, const char* rangeName=0) const;
    Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const ;

    Bool_t setData(RooAbsData& data, Bool_t cloneData=kTRUE) ;

    virtual std::list<Double_t>* binBoundaries(RooAbsRealLValue& /*obs*/, Double_t /*xlo*/, Double_t /*xhi*/) const ;
    virtual std::list<Double_t>* plotSamplingHint(RooAbsRealLValue& /*obs*/, Double_t /*xlo*/, Double_t /*xhi*/) const ; 
    Bool_t isBinnedDistribution(const RooArgSet& obs) const;

    virtual void enableOffsetting(Bool_t) ;
    

    RooAbsPdf * _pdf;
    std::map<int, RooDataHist*>  _datasets;
    RooRealVar * _MH;
    RooRealVar * _mgg;
    std::map<int, LCRooChi2Var*> _chi2map;



  protected:

    RooArgList _ownedList ;// List of owned components
    RooListProxy _set ;// set of terms to be summed
    mutable TIterator* _setIter ;//! Iterator over set

    class CacheElem : public RooAbsCacheElement {
      public:
        virtual ~CacheElem();
        // Payload
        RooArgList _I ;
        virtual RooArgList containedArgs(Action) ;
    };
    mutable RooObjCacheManager _cacheMgr ; // The cache manager

    Double_t evaluate() const;

    ClassDef(LCRooAddition,2) // Sum of RooAbsReal objects
};

#endif
