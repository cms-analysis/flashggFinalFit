#include "../interface/WSTFileWrapper.h"

#include <sstream>
#include <iostream>

WSTFileWrapper::WSTFileWrapper( std::string files, std::string wsname ) {
  std::stringstream ss(files);
  while( ss.good() ) {
    std::string substr;
    getline( ss, substr, ',' );
    fnList.push_back( substr );
  }
  wsName_ = wsname;

  std::cout << "inside WST contructor, about to loop over files" << std:: endl;
  for ( std::vector<std::string>::iterator fn = fnList.begin() ; fn != fnList.end() ; fn++ ) {
    fileList.push_back( TFile::Open(fn->c_str()) );
    if (fileList.back() == 0) {
      std::cout << "[WSTFileWrapper] got 0 for what should be this file: " << (*fn) << std::endl;
    } else if (fileList.back()->IsZombie()) {
      std::cout << "[WSTFileWrapper] got that this file is a zombie: " << (*fn) << std::endl;
    } else {
      // this is very verbose otherwise!
      std::cout << "[WSTFileWrapper] successfully opened this file: " << (*fn) << std::endl;
    }
    //FIXME this is the part that needs to be removed, due to memory issues
    // try to just access when necessary instead
    // for now keep the wsList and just add the first one
    // useful e.g. for keeping existing constructors, and accessing just the necessary vars (only need one workspace for that)
    if( fn == fnList.begin() ) { 
      wsList.push_back((RooWorkspace*)fileList.back()->Get(wsname.c_str()));
      if (wsList.back() == 0) {
        std::cout << "[WSTFileWrapper] on file " << (*fn) << " failed to obtain workspace named: " << wsname << std::endl;
      } else {
        // this is very verbose otherwise!
        std::cout << "[WSTFileWrapper] on file " << (*fn) << " opened workspace named: " << wsname << std::endl;
      }
    }
  }
  std::cout << "inside WST contructor, done loop over files" << std:: endl;
}

WSTFileWrapper::WSTFileWrapper( TFile *tf ,RooWorkspace *inWS ) {
  wsName_ = inWS->GetName();
  wsList.push_back(inWS);
  fnList.push_back("current file");
  fileList.push_back(tf);
}

WSTFileWrapper::WSTFileWrapper( RooWorkspace *inWS ) {
  TFile *outF = new TFile("WSTFileWrapper.root","RECREATE");
  wsName_ = inWS->GetName();
  wsList.push_back(inWS);
  fnList.push_back("current file");
  fileList.push_back(outF);
}


RooRealVar* WSTFileWrapper::var(std::string varName) {
  fileList[0]->cd();
  return wsList[0]->var(varName.c_str());
}

std::pair<std::string,std::string> WSTFileWrapper::convertTemplatedName(std::string dataName) {
  TString theDataName = TString(dataName);
  std::string theProcName = "";
  std::map<std::string,std::string> tpMap;
  tpMap["GG2H"] = "ggh";
  tpMap["VBF"] = "vbf";
  tpMap["TTH"] = "tth";
  tpMap["QQ2HLNU"] = "wh";
  tpMap["QQ2HLL"] = "zh";
  tpMap["WH2HQQ"] = "wh";
  tpMap["ZH2HQQ"] = "zh";
  tpMap["testBBH"] = "bbh";
  tpMap["testTHW"] = "th";
  tpMap["testTHQ"] = "th";
  for( std::map<std::string,std::string>::iterator it = tpMap.begin(); it != tpMap.end(); it++ ) {
    if( theDataName.BeginsWith(it->first) ) { 
      TString theDataNameCopy = theDataName;
      //dataset always looks like eg wh_125_13TeV_RECO_1J_PTH_120_200, and input is eg QQ2HLL_0J_125_13TeV_RECO_1J_PTH_120_200
      theDataNameCopy.Resize( theDataName.Index("_13TeV_")-4 );
      theProcName = theDataNameCopy.Data();
      theDataName.Replace( 0, theProcName.size(), it->second );
    }
  }
  std::pair<std::string,std::string> thePair;
  thePair.first  = theDataName.Data();
  thePair.second = theProcName;
  return thePair;
}

RooAbsData* WSTFileWrapper::data(std::string dataName) {
  std::pair<std::string,std::string> thePair = convertTemplatedName(dataName);
  std::string newDataName = thePair.first;
  std::string newProcName = thePair.second;
  RooAbsData* result = 0;
  bool complained_yet = 0;
  for( unsigned i=0; i<fileList.size(); i++ ) {
    TString tempFileName = fnList[i];
    if( tempFileName.Index(newProcName) < 0 ) { continue; }
    fileList[i]->cd();
    RooAbsData* this_result = (RooAbsData*)((RooWorkspace*)fileList[i]->Get(wsName_.c_str()))->data(newDataName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsDatas from the file list with the same name: " <<  newDataName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsData from " << fnList[i] << " with name " << newDataName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsData with name " << newDataName << std::endl;
  }
  return result;
}

RooAbsPdf* WSTFileWrapper::pdf(std::string pdfName) {
  RooAbsPdf* result = 0;
  bool complained_yet = 0;
  for( unsigned i=0; i<fileList.size(); i++ ) {
    fileList[i]->cd();
    RooAbsPdf* this_result = (RooAbsPdf*)((RooWorkspace*)fileList[i]->Get(wsName_.c_str()))->pdf(pdfName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsPdfs from the file list with the same name: " <<  pdfName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsPdf from " << fnList[i] << " with name " << pdfName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsPdf with name " << pdfName << std::endl;
  }
  return result;
}

RooCategory* WSTFileWrapper::cat(std::string catName) {
  RooCategory* result = 0;
  bool complained_yet = 0;
  for( unsigned i=0; i<fileList.size(); i++ ) {
    fileList[i]->cd();
    RooCategory* this_result = (RooCategory*)((RooWorkspace*)fileList[i]->Get(wsName_.c_str()))->cat(catName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooCategories from the file list with the same name: " <<  catName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooCategory from " << fnList[i] << " with name " << catName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooCategory with name " << catName << std::endl;
  }
  return result;
}

RooAbsReal* WSTFileWrapper::function(std::string functionName) {
  RooAbsReal* result = 0;
  bool complained_yet = 0;
  for( unsigned i=0; i<fileList.size(); i++ ) {
    fileList[i]->cd();
    RooAbsReal* this_result = (RooAbsReal*)((RooWorkspace*)fileList[i]->Get(wsName_.c_str()))->function(functionName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsReals from the file list with the same name: " <<  functionName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsData from " << fnList[i] << " with name " << functionName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsReal with name " << functionName << std::endl;
  }
  return result;
}

void WSTFileWrapper::Close() {
  for( unsigned i=0; i<fileList.size(); i++ ) {
    fileList[i]->Close();
  }
}
