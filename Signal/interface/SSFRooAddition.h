 /*****************************************************************************
* Project: RooFit *
* Package: RooFitCore *
*File: $Id: SSFRooAddition.h,v 1.3 2007/05/11 09:11:30 verkerke Exp $
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

//Modified version of RooAddition class, where the evaluation of the value allows one to change the value of the MH variable between items.

#ifndef SSFROO_ADDITION
#define SSFROO_ADDITION

#include "RooAbsReal.h"
#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooListProxy.h"
#include "RooObjCacheManager.h"
#include "../interface/SSFRooChi2Var.h"

class RooRealVar;
class RooArgList ;

class SSFRooAddition : public RooAbsReal {
  public:

    SSFRooAddition() ;
    SSFRooAddition(const char* name, const char* title, RooAbsPdf* pdf, std::map<int, RooDataHist*> datasets, RooRealVar* MH, RooRealVar *mgg ) ;
    SSFRooAddition(const char *name, const char *title, const RooArgList& sumSet, Bool_t takeOwnerShip=kFALSE) ;
    SSFRooAddition(const char *name, const char *title, const RooArgList& sumSet1, const RooArgList& sumSet2, Bool_t takeOwnerShip=kFALSE) ;
    virtual ~SSFRooAddition() ;

    SSFRooAddition(const SSFRooAddition& other, const char* name = 0);
    virtual TObject* clone(const char* newname) const { return new SSFRooAddition(*this, newname); }

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
    std::map<int, SSFRooChi2Var*> _chi2map;



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

    ClassDef(SSFRooAddition,2) // Sum of RooAbsReal objects
};

#endif
