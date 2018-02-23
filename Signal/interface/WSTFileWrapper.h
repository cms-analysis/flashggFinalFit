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
    RooRealVar* var(std::string);
    RooAbsPdf* pdf(std::string);
    RooCategory* cat(std::string);
    RooAbsData* data(std::string);
    RooAbsReal* function(std::string);
    std::pair<std::string,std::string> convertTemplatedName(std::string);
    void Close();
  private:
    std::vector<std::string> fnList;
    std::vector<TFile*> fileList;
    std::vector<RooWorkspace*> wsList;
    std::string wsName_;
};

#endif
