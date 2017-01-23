#ifndef SimultaneousFit_h 
#define SimultaneousFit_h

#include <iostream>
#include <vector>
#include <string>
#include <map>

#include "RooAbsReal.h"
#include "RooGaussian.h"
#include "RooAddPdf.h"
#include "RooDataSet.h"
#include "RooDataHist.h"
#include "RooRealVar.h"
#include "RooFitResult.h"
#include "RooHist.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooSpline1D.h"
#include "HiggsAnalysis/GBRLikelihood/interface/RooDoubleCBFast.h"

class SimultaneousFit {

  public:

    SimultaneousFit(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, std::vector<int> skipMasses, bool binnedFit, int binso, std::vector<int> massList, std::string cat, std::string proc, std::string outdir, int maxOrder);
    ~SimultaneousFit();

    void buildSumOfGaussians(std::string name, int nGaussians,  bool recursive=false ,  bool forceFracUnity=false);
    void buildDCBplusGaussian(std::string name, bool recursive=false);
    void loadPriorConstraints(std::string filename, float constraintValue);
    void saveParamsToFile(std::string filename);
    void saveParamsToFileAtMH(std::string filename, int setMH);
    std::map<int,std::map<std::string,RooRealVar*> > getFitParams();
		void printFitParams();
    float getChi2( RooHist* data, RooCurve *pdf);
    void setDatasets(std::map<int,RooDataSet*> data);
    void setDatasetsSTD(std::map<int,RooDataSet*> data);
    void addDataset(int mh, RooDataSet *data);
    void runFits(int ncpu, std::string outdir, float iterativeFitConstraint);
    int  isDCBsafe(RooDoubleCBFast* dcb);
    void plotFits(std::string name, std::string rvwn="");
    void setVerbosity(int v);
    RooDataSet* mergeNormalisedDatasets (std::map<int,RooDataSet*> data);
    RooDataSet* normaliseDatasets (RooDataSet* data);
    std::map<std::string,RooSpline1D*> getSplines();

    void setFitParams(std::map<int,std::map<std::string,RooRealVar*> >& pars );
    RooArgSet* getListOfPolyVars(){ return listOfPolyVars_;} 
  private:

    RooRealVar *mass;
    RooRealVar *MH;
    RooArgSet *listOfPolyVars_;
    std::map<int,RooAbsPdf*> allPdfs;
    std::map<int,RooDataSet*> datasets; 
    std::map<int,RooDataSet*> datasetsSTD; 
    std::map<int,std::map<std::string,RooRealVar*> > fitParams;
    std::map<int,std::map<std::string,RooAbsReal*> > fitUtils;
    std::map<int,std::map<std::string,RooAbsPdf*> > initialGaussians;
    std::map<int,RooFitResult*> fitResults;
    int mhLow_;
    int maxOrder_;
    int mhHigh_;
		std::vector<int> skipMasses_;
    std::vector<int> allMH_;
    std::vector<int> getAllMH();
		bool skipMass(int mh);
    int verbosity_;
    bool binnedFit_;
    int bins_;
    std::string cat_;
    std::string proc_;
    std::string outdir_;

};

#endif
