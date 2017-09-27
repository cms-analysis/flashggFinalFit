#ifndef FinalModelConstruction_h 
#define FinalModelConstruction_h

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>

#include "TGraph.h"

#include "RooAbsReal.h"
#include "RooAddition.h"
#include "RooGaussian.h"
#include "RooAddPdf.h"
#include "RooExtendPdf.h"
#include "RooDataSet.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "RooConstVar.h"
#include "RooWorkspace.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"
#include "HiggsAnalysis/GBRLikelihood/interface/RooDoubleCBFast.h"
#include "Normalization_8TeV.h"

class FinalModelConstruction {

  public:
    
    FinalModelConstruction( std::vector<int> massList, RooRealVar *massVar, RooRealVar *MHvar, RooRealVar *intL, int mhLow, int mhHigh, std::string proc, std::string cat, bool doSecMods, std::string systematicsFileName, std::vector<int> skipMasses, int verbosity, std::vector<std::string> procsList, std::vector<std::string> flashggCats , string outDir,bool isProblemCategory,bool isCB=false, int sqrts=13, bool quadraticSigmaSum=false);
    ~FinalModelConstruction();

		void loadSignalSystematics(std::string filename);
		void printSignalSystematics();

    void setSecondaryModelVars(RooRealVar *mh_sm, RooRealVar *deltam, RooAddition *mh_2, RooRealVar *width);

    void buildRvWvPdf(std::string name, int nGrv, int nGwv, bool recusive, bool useDCBplusGaus);
    void buildStdPdf(std::string name, int nGaussians, bool recursive);
    std::vector<RooAbsPdf*> buildPdf(std::string name, int nGaussians, bool recursive, std::map<std::string,RooSpline1D*> splines, string add="");
    std::vector<RooAbsPdf*> build_DCBpGaus_Pdf(std::string name, int nGaussians, bool recursive, std::map<std::string,RooSpline1D*> splines, string add="");
    void getRvFractionFunc(std::string name);
    void setupSystematics();
    void getNormalization();

		RooAbsReal *getMeanWithPhotonSyst(RooAbsReal *dm, string name, bool isMH2=false, bool isMHSM=false);
		RooAbsReal *getSigmaWithPhotonSyst(RooAbsReal *sig_fit, string name);
		RooAbsReal *getRateWithPhotonSyst(string name);
    
		void setRVsplines(std::map<std::string,RooSpline1D*> splines);
    void setWVsplines(std::map<std::string,RooSpline1D*> splines);
    void setSTDsplines(std::map<std::string,RooSpline1D*> splines);

    void setRVdatasets(std::map<int,RooDataSet*> data);
    void setWVdatasets(std::map<int,RooDataSet*> data);
    void setFITRVdatasets(std::map<int,RooDataSet*> data);
    void setFITWVdatasets(std::map<int,RooDataSet*> data);
    void setSTDdatasets(std::map<int,RooDataSet*> data);
    void setFITdatasets(std::map<int,RooDataSet*> data);
		void makeSTDdatasets();
		void makeFITdatasets();

		void setHighR9cats(std::string catString);
		void setLowR9cats(std::string catString);

    void plotPdf(std::string outDir);

    void save(RooWorkspace *work);

  private:
    
    RooRealVar *mass;
    RooRealVar *MH;
    RooRealVar *intLumi;
    int mhLow_;
    int mhHigh_;
    std::string proc_;
    std::string cat_;
    std::string outDir_;
    int nIncCats_;
    bool isProblemCategory_;
    bool doSecondaryModels;
    bool secondaryModelVarsSet;
    bool isCutBased_;
		bool is2011_;
		bool is2012_;
		bool isFlashgg_;
		int sqrts_;
		bool quadraticSigmaSum_;
		std::vector<int> skipMasses_;
    std::vector<int> allMH_;
    std::vector<int> getAllMH();
    std::vector<string> flashggCats_;
		bool skipMass(int mh);
    int verbosity_;
    Normalization_8TeV *norm;
    ofstream paramDump_;

    std::map<std::string,RooSpline1D*> stdSplines;
    std::map<std::string,RooSpline1D*> rvSplines;
    std::map<std::string,RooSpline1D*> wvSplines;
    std::map<int,RooDataSet*> rvDatasets;
    std::map<int,RooDataSet*> wvDatasets;
    std::map<int,RooDataSet*> stdDatasets;
    std::map<int,RooDataSet*> rvFITDatasets;
    std::map<int,RooDataSet*> wvFITDatasets;
    std::map<int,RooDataSet*> fitDatasets;
   
	 	// vertex and r9 nuisances
    RooRealVar *vertexNuisance;
		RooRealVar *r9barrelNuisance;
		RooRealVar *r9mixedNuisance;
		std::vector<int> highR9cats;
		std::vector<int> lowR9cats;
    RooSpline1D *rvFracFunc;
    RooSpline1D *rvFracFunc_SM;
    RooSpline1D *rvFracFunc_2;
    RooSpline1D *rvFracFunc_NW;

    RooAbsPdf *finalPdf;
    RooAbsReal *finalNorm;
    RooAbsReal *finalNormThisLum;
    RooExtendPdf *extendPdfRel;
    RooExtendPdf *extendPdf;
    // secondary models
    RooAbsPdf *finalPdf_SM;
    RooAbsPdf *finalPdf_2;
    RooAbsPdf *finalPdf_NW;
    RooAbsReal *finalNorm_SM;
    RooAbsReal *finalNorm_2;
    RooAbsReal *finalNorm_NW;

    bool systematicsSet_;
    bool rvFractionSet_;
		std::vector<std::string> procs_;

    RooSpline1D *graphToSpline(string name, TGraph *graph);
    RooSpline1D *graphToSpline(string name, TGraph *graph, RooAbsReal *var);

    std::map<std::string,RooSpline1D*> xsSplines;
    RooSpline1D *brSpline;
    // secondary models
    std::map<std::string,RooSpline1D*> xsSplines_SM;
    RooSpline1D *brSpline_SM;
    std::map<std::string,RooSpline1D*> xsSplines_2;
    RooSpline1D *brSpline_2;
    std::map<std::string,RooSpline1D*> xsSplines_NW;
    RooSpline1D *brSpline_NW;

    RooRealVar *MH_SM;
    RooRealVar *DeltaM;
    RooAddition *MH_2;
    RooRealVar *higgsDecayWidth;

		// photon systematic stuff
		std::vector<std::string> photonCatScales;
		std::vector<std::string> photonCatScalesCorr;
		std::vector<std::string> photonCatSmears;
		std::vector<std::string> photonCatSmearsCorr;
		std::vector<std::string> globalScales;
		std::vector<std::string> globalScalesCorr;
		// these are required to know specific options about further scaling 
		std::map<std::string,std::vector<std::pair<string,float> > > globalScalesOpts;
		std::map<std::string,std::vector<std::pair<string,float> > > globalScalesCorrOpts;
		std::vector<std::string> systematicsList;
		std::vector<float> systematicsCorr;
		std::vector<int> systematicsIdx;
		
		std::vector<std::string> photonCats;
		std::map<std::string,std::map<int,std::map<std::string,double> > > meanSysts;
		std::map<std::string,std::map<int,std::map<std::string,double> > > sigmaSysts;
		std::map<std::string,std::map<int,std::map<std::string,double> > > rateSysts;

		std::map<string,RooAbsReal*> photonSystematics;
		std::map<string,RooConstVar*> photonSystematicConsts;

		// utility funcs
		void addToSystematicsList(std::vector<std::string> systs);
		void addToSystematicsList(vector<string>::iterator begin, vector<string>::iterator end);
		
		bool isGlobalSyst(std::string name);
		bool isPerCatSyst(std::string name);
		bool isHighR9cat();
		bool isLowR9cat();
		float getRequiredAddtionalGlobalScaleFactor(std::string syst);
		void stripSpace(std::string &line);
		void printVec(std::vector<std::string> vec);
		void printSystMap(std::map<std::string,std::map<int,std::map<std::string,double> > > &theMap);
		void addToSystMap(std::map<std::string,std::map<int,std::map<std::string,double> > > &theMap, string proc, int diphotonCat, string phoSystName, double var);

};

#endif

