#include "TFile.h"
#include "TObject.h"
#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooRealVar.h"
#include <string>
#include <list>
#include <map>
#ifndef WSTFILEWRAPPER 
#define WSTFILEWRAPPER 


class WSTFileWrapper  {
  public:
    WSTFileWrapper(std::string, std::string);
    WSTFileWrapper( TFile*, RooWorkspace *);
    WSTFileWrapper( RooWorkspace *);
    RooWorkspace* getSpecificWorkspace(std::string);
    RooWorkspace* getSpecificWorkspace(int);
    RooRealVar* var(std::string);
    RooAbsPdf* pdf(std::string);
    RooAbsPdf* pdf(std::string, std::string);
    RooCategory* cat(std::string);
    RooCategory* cat(std::string, std::string);
    RooAbsData* data(std::string);
    RooAbsData* data(std::string, std::string);
    RooAbsReal* function(std::string);
    RooAbsReal* function(std::string, std::string);
    std::pair<std::string,std::string> convertTemplatedName(std::string);
    std::string fileToKey(std::string);
    int nFiles() { return fileList.size(); }
    void Close();
  private:
    std::vector<std::string> fnList;
    std::map<std::string,TFile*> fileList;
    std::vector<RooWorkspace*> wsList;
    std::string wsName;
};

#endif
