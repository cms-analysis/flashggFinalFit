 /*****************************************************************************
* Project: RooFit *
* Package: RooFitCore *
*File: $Id: SSFRooChi2Var.h,v 1.12 2007/05/11 09:11:30 verkerke Exp $
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

//modified version of RooChi2Var to avoid needless failure of fits because of low yield bins in the tails

#ifndef SSF_ROO_CHI2_VAR
#define SSF_ROO_CHI2_VAR

#include "RooAbsOptTestStatistic.h"
#include "RooCmdArg.h"
#include "RooDataHist.h"
#include "RooAbsPdf.h"

class SSFRooChi2Var : public RooAbsOptTestStatistic {
  public:

    // Constructors, assignment etc
    SSFRooChi2Var(const char *name, const char* title, RooAbsReal& func, RooDataHist& data,
        const RooCmdArg& arg1, const RooCmdArg& arg2=RooCmdArg::none(),const RooCmdArg& arg3=RooCmdArg::none(),
        const RooCmdArg& arg4=RooCmdArg::none(), const RooCmdArg& arg5=RooCmdArg::none(),const RooCmdArg& arg6=RooCmdArg::none(),
        const RooCmdArg& arg7=RooCmdArg::none(), const RooCmdArg& arg8=RooCmdArg::none(),const RooCmdArg& arg9=RooCmdArg::none()) ;

    SSFRooChi2Var(const char *name, const char* title, RooAbsPdf& pdf, RooDataHist& data,
        const RooCmdArg& arg1, const RooCmdArg& arg2=RooCmdArg::none(),const RooCmdArg& arg3=RooCmdArg::none(),
        const RooCmdArg& arg4=RooCmdArg::none(), const RooCmdArg& arg5=RooCmdArg::none(),const RooCmdArg& arg6=RooCmdArg::none(),
        const RooCmdArg& arg7=RooCmdArg::none(), const RooCmdArg& arg8=RooCmdArg::none(),const RooCmdArg& arg9=RooCmdArg::none()) ;

    enum FuncMode { Function, Pdf, ExtendedPdf } ;

    SSFRooChi2Var(const char *name, const char *title, RooAbsPdf& pdf, RooDataHist& data,
        Bool_t extended=kFALSE, const char* rangeName=0, const char* addCoefRangeName=0, 
        Int_t nCPU=1, RooFit::MPSplit interleave=RooFit::BulkPartition, Bool_t verbose=kTRUE, Bool_t splitCutRange=kTRUE, RooDataHist::ErrorType=RooDataHist::SumW2) ;

    SSFRooChi2Var(const char *name, const char *title, RooAbsReal& func, RooDataHist& data,
        const RooArgSet& projDeps, FuncMode funcMode, const char* rangeName=0, const char* addCoefRangeName=0, 
        Int_t nCPU=1, RooFit::MPSplit interleave=RooFit::BulkPartition, Bool_t verbose=kTRUE, Bool_t splitCutRange=kTRUE, RooDataHist::ErrorType=RooDataHist::SumW2) ;

    SSFRooChi2Var(const SSFRooChi2Var& other, const char* name=0);
    virtual TObject* clone(const char* newname) const { return new SSFRooChi2Var(*this,newname); }

    virtual RooAbsTestStatistic* create(const char *name, const char *title, RooAbsReal& pdf, RooAbsData& dhist,
        const RooArgSet& projDeps, const char* rangeName=0, const char* addCoefRangeName=0, 
        Int_t nCPU=1, RooFit::MPSplit interleave=RooFit::BulkPartition,Bool_t verbose=kTRUE, Bool_t splitCutRange=kTRUE, Bool_t = kFALSE) {
      // Virtual constructor
      return new SSFRooChi2Var(name,title,(RooAbsPdf&)pdf,(RooDataHist&)dhist,projDeps,_funcMode,rangeName,
          addCoefRangeName,nCPU,interleave,verbose, splitCutRange,_etype) ;
    }

    virtual ~SSFRooChi2Var();

    virtual Double_t defaultErrorLevel() const { 
      // The default error level for MINUIT error analysis for a chi^2 is 1.0
      return 1.0 ; 
    }
    RooDataHist*  _data;
  protected:

    static RooArgSet _emptySet ;// Supports named argument constructor

    RooDataHist::ErrorType _etype ; // Error type store in associated RooDataHist
    FuncMode _funcMode ;// Function, P.d.f. or extended p.d.f?

    virtual Double_t evaluatePartition(Int_t firstEvent, Int_t lastEvent, Int_t stepSize) const ;

    ClassDef(SSFRooChi2Var,1) // Chi^2 function of p.d.f w.r.t a binned dataset
};


#endif
