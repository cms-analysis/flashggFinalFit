#include "TFile.h"
#include "TObject.h"
#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooRealVar.h"
#include <string>
#include <list>

class WSTFileWrapper  {
  public:
    WSTFileWrapper(std::string, std::string);
  //    TObject * Get(std::string);
    RooRealVar* var(std::string);
    RooAbsData* data(std::string);
    std::list<RooAbsData*> allData();
    void Close();
  private:
    std::vector<std::string> fnList;
    std::vector<TFile*> fileList;
    std::vector<RooWorkspace*> wsList;
};
