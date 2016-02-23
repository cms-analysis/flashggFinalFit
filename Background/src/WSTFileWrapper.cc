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

  for ( std::vector<std::string>::iterator fn = fnList.begin() ; fn != fnList.end() ; fn++ ) {
    fileList.push_back(TFile::Open(fn->c_str()));
    if (fileList.back() == 0) {
      std::cout << "[WSTFileWrapper] got 0 for what should be this file: " << (*fn) << std::endl;
    } else if (fileList.back()->IsZombie()) {
      std::cout << "[WSTFileWrapper] got that this file is a zombie: " << (*fn) << std::endl;
    } else {
      std::cout << "[WSTFileWrapper] successfully opened this file: " << (*fn) << std::endl;
    }
    wsList.push_back((RooWorkspace*)fileList.back()->Get(wsname.c_str()));
    if (wsList.back() == 0) {
      std::cout << "[WSTFileWrapper] on file " << (*fn) << " failed to obtain workspace named: " << wsname << std::endl;
    } else {
      std::cout << "[WSTFileWrapper] on file " << (*fn) << " opened workspace named: " << wsname << std::endl;
    }
  }
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

RooArgSet WSTFileWrapper::allVars() {
  RooArgSet result;
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    fileList[0]->cd(); //only need 0th entry since they should all be same
    RooArgSet ras = wsList[0]->allVars();
    return ras;
    break;
  }
  return result;
}

RooRealVar* WSTFileWrapper::var(std::string varName) {
  fileList[0]->cd();
  return wsList[0]->var(varName.c_str());
}

RooAbsData* WSTFileWrapper::data(std::string dataName) {
  RooAbsData* result = 0;
  bool complained_yet = 0;
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    fileList[i]->cd();
    RooAbsData* this_result = (RooAbsData*)wsList[i]->data(dataName.c_str());
    if (result && this_result && !complained_yet) {
      std::cout << "[WSTFileWrapper] Uh oh, multiple RooAbsDatas from the file list with the same name: " <<  dataName << std::endl;
      complained_yet = true;
    }
    if (this_result) {
      result = this_result;
      std::cout << "[WSTFileWrapper] Got non-zero RooAbsData from " << fnList[i] << " with name " << dataName << std::endl;
    }
  }
  if (!result) {
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsData with name " << dataName << std::endl;
  }
  return result;
}
    
RooAbsPdf* WSTFileWrapper::pdf(std::string pdfName) {
  RooAbsPdf* result = 0;
  bool complained_yet = 0;
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    fileList[i]->cd();
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
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooAbsPdf with name " << pdfName << std::endl;
  }
  return result;
}

RooCategory* WSTFileWrapper::cat(std::string catName) {
  RooCategory* result = 0;
  bool complained_yet = 0;
  for (unsigned int i = 0 ; i < fileList.size() ; i++) {
    fileList[i]->cd();
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
    std::cout << "[WSTFileWrapper] Uh oh, never got a good RooCategory with name " << catName << std::endl;
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
