#include "TFile.h"
#include "TObject.h"
#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooRealVar.h"
#include "RooArgSet.h"
#include <string>
#include <list>

class WSTFileWrapper  {
  public:
    WSTFileWrapper(std::string, std::string);
  //    TObject * Get(std::string);
    RooRealVar* var(std::string);
    RooAbsPdf* pdf(std::string);
    RooCategory* cat(std::string);
    RooAbsData* data(std::string);
    std::list<RooAbsData*> allData();
    RooArgSet allVars();
    void Close();
  private:
    std::vector<std::string> fnList;
    std::vector<TFile*> fileList;
    std::vector<RooWorkspace*> wsList;
};
