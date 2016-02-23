#ifndef Packager_h 
#define Packager_h

#include <iostream>
#include <vector>
#include <string>
#include <map>

#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooDataSet.h"

#include "Normalization_8TeV.h"

#include "WSTFileWrapper.h"

class Packager {

  public:

    Packager(WSTFileWrapper *wst, RooWorkspace *saveWS, std::vector<std::string> procs, int nCats, int mhLow, int mhHigh, std::vector<int> skipMasses, int sqrts=-1, bool skipPlots=false, string outDir="plots",
	     RooWorkspace *mergeWs=0, const std::vector<int>& cats=std::vector<int>() ,const std::vector<string>& flashggCats=std::vector<string>());
   // Packager(WSTFileWrapper *ws, std::vector<std::string> procs, int nCats, int mhLow, int mhHigh, std::vector<int> skipMasses, int sqrts=-1, bool skipPlots=false, string outDir="plots",
	   //  RooWorkspace *mergeWs=0, const std::vector<int>& cats=std::vector<int>() ,const std::vector<string>& flashggCats=std::vector<string>());
    ~Packager();

    void packageOutput( bool split, string process="", string tag=""); //split indicates whwether to consider all tags  and procs or just one proc/tag 
		void makePlots();
		void makePlot(RooRealVar *mass, RooRealVar *MH, RooAddPdf *pdf, std::map<int,RooDataSet*> data, std::string name);

  private:
   // RooWorkspace *outWS;
    WSTFileWrapper *WS;
    RooWorkspace *mergeWS;
    RooWorkspace *saveWS;
    std::vector<std::string> procs_;
    int nCats_;
    std::vector<int> cats_;
    std::vector<string> flashggCats_;
    int mhLow_;
    int mhHigh_;
    bool is2011_;
		bool skipPlots_;
    string outDir_;
    int sqrts_;
    std::vector<int> skipMasses_;
    bool skipMass(int mh);
    Normalization_8TeV *normalization;

};
#endif
