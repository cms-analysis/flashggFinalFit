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

  std::cout << "inside WST contructor, about to loop over files" << std:: endl;
  for ( std::vector<std::string>::iterator fn = fnList.begin() ; fn != fnList.end() ; fn++ ) {
    fileList.push_back(TFile::Open(fn->c_str()));
    if (fileList.back() == 0) {
      std::cout << "[WSTFileWrapper] got 0 for what should be this file: " << (*fn) << std::endl;
    } else if (fileList.back()->IsZombie()) {
      std::cout << "[WSTFileWrapper] got that this file is a zombie: " << (*fn) << std::endl;
    } else {
      // this is very verbose otherwise!
			std::cout << "[WSTFileWrapper] successfully opened this file: " << (*fn) << std::endl;
    }
    wsList.push_back((RooWorkspace*)fileList.back()->Get(wsname.c_str()));
    if (wsList.back() == 0) {
      std::cout << "[WSTFileWrapper] on file " << (*fn) << " failed to obtain workspace named: " << wsname << std::endl;
    } else {
      // this is very verbose otherwise!
      std::cout << "[WSTFileWrapper] on file " << (*fn) << " opened workspace named: " << wsname << std::endl;
    }
  }
  std::cout << "inside WST contructor, done loop over files" << std:: endl;
}

WSTFileWrapper::WSTFileWrapper( TFile *tf ,RooWorkspace *inWS ) {
wsList.push_back(inWS);
fileList.push_back(tf);
fnList.push_back("current file");
}

std::list<RooAbsData*> WSTFileWrapper::allData() {
  std::list<RooAbsData*> result;
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    fileList[i]->cd();
    std::list<RooAbsData*> this_result = wsList[i]->allData();
    result.splice(result.end(),this_result);
  }
  return result;
}

WSTFileWrapper::WSTFileWrapper( RooWorkspace *inWS ) {
TFile *outF = new TFile("WSTFileWrapper.root","RECREATE");
wsList.push_back(inWS);
fileList.push_back(outF);
fnList.push_back("current file");
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
      theProcName = it->first;
      theDataName.Replace( 0, it->first.size(), it->second );
      theDataName.ReplaceAll("_FWDH","");
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
  assert(wsList.size() == fileList.size());
  for (unsigned int i = 0 ; i < wsList.size() ; i++) {
    if( fnList[i] != "current file" ) {
      if(fnList[i].find(newProcName)==std::string::npos && newProcName!="") continue;
      bool procIsFwd = dataName.find("FWD")!=std::string::npos;
      bool fileIsFwd = fnList[i].find("FWD")!=std::string::npos;
      if( (procIsFwd&&!fileIsFwd) || (!procIsFwd&&fileIsFwd) ) continue;
    }
    fileList[i]->cd();
    RooAbsData* this_result = (RooAbsData*)wsList[i]->data(newDataName.c_str());
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
  for (unsigned int i = 0 ; i < wsList.size() ; i++) {
    if (fileList.size()>i) fileList[i]->cd();
    RooAbsPdf* this_result = (RooAbsPdf*)wsList[i]->pdf(pdfName.c_str());
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
    //std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsPdf with name " << pdfName << std::endl;
  }
  return result;
}

RooCategory* WSTFileWrapper::cat(std::string catName) {
  RooCategory* result = 0;
  bool complained_yet = 0;
  for (unsigned int i = 0 ; i < wsList.size() ; i++) {
    if (fileList.size()>i) fileList[i]->cd();
    RooCategory* this_result = (RooCategory*)wsList[i]->cat(catName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooCategorys from the file list with the same name: " <<  catName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooCategory from " << fnList[i] << " with name " << catName << std::endl;
    }
  }
  if (!result) {
    //std::cout << "[WSTFileWrapper] Uh oh, never got a good RooCategory with name " << catName << std::endl;
  }
  return result;
}

RooAbsReal* WSTFileWrapper::function(std::string functionName) {
  RooAbsReal* result = 0;
  bool complained_yet = 0;
  for (unsigned int i = 0 ; i < wsList.size() ; i++) {
    if (fileList.size()>i) fileList[i]->cd();
    RooAbsReal* this_result = (RooAbsReal*)wsList[i]->function(functionName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsReals from the file list with the same name: " <<  functionName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsReal from " << fnList[i] << " with name " << functionName << std::endl;
    }
  }
  if (!result) {
    //std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsReal with name " << functionName << std::endl;
  }
  return result;
}
/*
TObject* WSTFileWrapper::Get(std::string namecycle) {
  TObject* result = 0;
  bool complained_yet = 0;
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    TObject* this_result = fileList[i]->Get(namecycle.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << " WSTFileWrapper: Uh oh, multiple TObjects from the file list with the same name: " <<  namecycle << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << " WSTFileWrapper: Got non-zero TObject from " << fnList[i] << std::endl;
    }
  }
  if (!result) {
    std::cout << " WSTFileWrapper: Uh oh, never got a good TObject " << std::endl;
  }
  return result;
}
*/

void WSTFileWrapper::Close() {
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    fileList[i]->Close();
  }
}

RooArgSet WSTFileWrapper::allVars(){

  RooArgSet result;
  //bool complained_yet = 0;
  for (unsigned int i = 0 ; i < wsList.size() ; i++) {
    if (fileList.size()>i) fileList[i]->cd();
    RooArgSet this_result = wsList[i]->allVars();
    result.add(this_result);
  }
 // if (!result) {
 //   std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsReal with name " << functionName << std::endl;
//  }
  return result;
}

RooArgSet WSTFileWrapper::allFunctions(){

  RooArgSet result;
  //bool complained_yet = 0;
  for (unsigned int i = 0 ; i < wsList.size() ; i++) {
    if (fileList.size()>i) fileList[i]->cd();
    RooArgSet this_result = wsList[i]->allFunctions();
    result.add(this_result);
  }
//  if (!result) {
  //  std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsReal with name " << functionName << std::endl;
 // }
  return result;
}



/*
#include "TFile.h"
#include "TObject.h"
#include <string>

class WSTFileWrapper  {
  public:
  WSTFileWrapper(string )
virtual TObject * Get();
void Close();
private:
vector<string> fnList;
vector<TFile*> fileList;
}

*/
