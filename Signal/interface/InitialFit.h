#ifndef InitialFit_h 
#define InitialFit_h

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

class InitialFit {

  public:

    InitialFit(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, std::vector<int> skipMasses, bool binnedFit, int binso, std::vector<int> massList);
    ~InitialFit();

    void buildDCBplusGaussian(std::string name);
    void buildSumOfGaussians(std::string name, int nGaussians, bool recursive=false, bool forceFracUnity=false);
    void loadPriorConstraints(std::string filename, float constraintValue);
    void saveParamsToFile(std::string filename);
    void saveParamsToFileAtMH(std::string filename, int setMH);
    std::map<int,std::map<std::string,RooRealVar*> > getFitParams();
		void printFitParams();
    void setDatasets(std::map<int,RooDataSet*> data);
    void setDatasetsSTD(std::map<int,RooDataSet*> data);
    void addDataset(int mh, RooDataSet *data);
    void runFits(int ncpu);
    void plotFits(std::string name, std::string rvwn="");
    void setVerbosity(int v);

    void setFitParams(std::map<int,std::map<std::string,RooRealVar*> >& pars );
    void printCorrMatrix(int mh);
  private:

    RooRealVar *mass;
    RooRealVar *MH;
    std::map<int,RooAbsPdf*> fitPdfs;
    std::map<int,RooDataSet*> datasets; 
    std::map<int,RooDataSet*> datasetsSTD; 
    std::map<int,std::map<std::string,RooRealVar*> > fitParams;
    std::map<int,std::map<std::string,RooAbsReal*> > fitUtils;
    std::map<int,std::map<std::string,RooGaussian*> > initialGaussians;
    std::map<int,RooFitResult*> fitResults;
    int mhLow_;
    int mhHigh_;
		std::vector<int> skipMasses_;
    std::vector<int> allMH_;
    std::vector<int> getAllMH();
		bool skipMass(int mh);
    int verbosity_;
    bool binnedFit_;
    int bins_;

};

#endif
