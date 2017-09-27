#include "TFile.h"
#include "TObject.h"
#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooRealVar.h"
#include <string>
#include <list>
#ifndef WSTFILEWRAPPER 
#define WSTFILEWRAPPER 


class WSTFileWrapper  {
  public:
    WSTFileWrapper(std::string, std::string);
    WSTFileWrapper( TFile*, RooWorkspace *);
    WSTFileWrapper( RooWorkspace *);
  //    TObject * Get(std::string);
    RooRealVar* var(std::string);
    RooAbsPdf* pdf(std::string);
    RooCategory* cat(std::string);
    RooAbsData* data(std::string);
    RooAbsReal* function(std::string);
    RooArgSet allVars();
    RooArgSet allFunctions();
    std::pair<std::string,std::string> convertTemplatedName(std::string);
    std::list<RooAbsData*> allData();
    std::vector<RooWorkspace*> getWsList(){ return wsList;}
    void Close();
  private:
    std::vector<std::string> fnList;
    std::vector<TFile*> fileList;
    std::vector<RooWorkspace*> wsList;
};

#endif
