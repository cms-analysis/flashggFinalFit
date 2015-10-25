#include <iostream>
#include <string>
#include <map>
#include <vector>

#include "TFile.h"
#include "TMath.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TLegend.h"

#include "TStopwatch.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooDataHist.h"
#include "RooAddPdf.h"
#include "RooGaussian.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "RooFitResult.h"
#include "RooPlot.h"
#include "RooMsgService.h"
#include "RooMinuit.h"

#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

using namespace std;
using namespace RooFit;
using namespace boost;
namespace po = boost::program_options;

string filename_;
string datfilename_;
string json_dict_;
string outdir_;
int mass_;
string procString_;
int ncats_;
bool recursive_=false;
string flashggCatsStr_;
vector<string> flashggCats_;
bool forceFracUnity_=false;
bool isFlashgg_;
bool verbose_;

void OptionParser(int argc, char *argv[]){
	po::options_description desc1("Allowed options");
	desc1.add_options()
		("help,h",                                                                                "Show help")
		("infilename,i", po::value<string>(&filename_),                                           "Input file name")
		("datfilename,d", po::value<string>(&datfilename_)->default_value("dat/config.dat"),      "Output configuration file")
		("outdir,o", po::value<string>(&outdir_)->default_value("plots"),      "Output configuration file")
		("json_dict,j", po::value<string>(&json_dict_)->default_value(""),      "Output configuration file")
		("mass,m", po::value<int>(&mass_)->default_value(125),                                    "Mass to run at")
		("procs,p", po::value<string>(&procString_)->default_value("ggh,vbf,wh,zh,tth"),          "Processes")
		("recursive",																																							"Recursive fraction")
		("forceFracUnity",																																				"Force fraction unity")
		("isFlashgg",	po::value<bool>(&isFlashgg_)->default_value(true),													"Use flashgg format")
		("verbose",	po::value<bool>(&verbose_)->default_value(false),													"Use flashgg format")
		("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg category names to consider")
		;

	po::options_description desc2("Options kept for backward compatibility");
	desc2.add_options()
		("ncats,n", po::value<int>(&ncats_)->default_value(9),																			"Number of cats (Set Automatically if using --isFlashgg 1)")
		;
	po::options_description desc("Allowed options");
	desc.add(desc1).add(desc2);

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,desc),vm);
	po::notify(vm);
	if (vm.count("help")){ cout << desc << endl; exit(1);}
	if (vm.count("recursive")) recursive_=true;
	if (vm.count("forceFracUnity")) forceFracUnity_=true;
}

RooAddPdf *buildSumOfGaussians(string name, RooRealVar *mass, RooRealVar *MH, int nGaussians){

	RooArgList *gaussians = new RooArgList();
	RooArgList *coeffs = new RooArgList();
	for (int g=0; g<nGaussians; g++){
		RooRealVar *dm = new RooRealVar(Form("dm_g%d",g),Form("dm_g%d",g),0.1,-5.*(1.+0.5*g),5.*(1.+0.5*g));
		RooAbsReal *mean = new RooFormulaVar(Form("mean_g%d",g),Form("mean_g%d",g),"@0+@1",RooArgList(*MH,*dm));
		RooRealVar *sigma = new RooRealVar(Form("sigma_g%d",g),Form("sigma_g%d",g),2.,0.7,5.*(1.+0.5*g));
		RooGaussian *gaus = new RooGaussian(Form("gaus_g%d",g),Form("gaus_g%d",g),*mass,*mean,*sigma);
		//tempFitParams.insert(pair<string,RooRealVar*>(string(dm->GetName()),dm));
		//tempFitParams.insert(pair<string,RooRealVar*>(string(sigma->GetName()),sigma));
		//tempFitUtils.insert(pair<string,RooAbsReal*>(string(mean->GetName()),mean));
		//tempGaussians.insert(pair<string,RooGaussian*>(string(gaus->GetName()),gaus));
		gaussians->add(*gaus);
		if (g<nGaussians-1) {
			RooRealVar *frac = new RooRealVar(Form("frac_g%d",g),Form("frac_g%d",g),0.1,0.01,0.99);
			//tempFitParams.insert(pair<string,RooRealVar*>(string(frac->GetName()),frac));
			coeffs->add(*frac);
		}
		if (g==nGaussians-1 && forceFracUnity_){
			string formula="1.";
			for (int i=0; i<nGaussians-1; i++) formula += Form("-@%d",i);
			RooAbsReal *recFrac = new RooFormulaVar(Form("frac_g%d",g),Form("frac_g%d",g),formula.c_str(),*coeffs);
			//tempFitUtils.insert(pair<string,RooAbsReal*>(string(recFrac->GetName()),recFrac));
			coeffs->add(*recFrac);
		}
	}
	RooAddPdf *tempSumOfGaussians = new RooAddPdf(name.c_str(),name.c_str(),*gaussians,*coeffs,recursive_);
	return tempSumOfGaussians;
}

void plot(string outPath, int mh, RooRealVar *var, RooAbsData *data, RooAbsPdf *pdf){

	TCanvas *canv = new TCanvas();
	RooPlot *plot = var->frame(Range(mh-10,mh+10));
	data->plotOn(plot);
	pdf->plotOn(plot);
	plot->Draw();
	canv->Print(Form("%s.pdf",outPath.c_str()));
}

double getMyNLL(RooRealVar *var, RooAbsPdf *pdf, RooDataHist *data){
	RooPlot *plot = var->frame();
	data->plotOn(plot);
	pdf->plotOn(plot);
	RooCurve *pdfCurve = (RooCurve*)plot->getObject(plot->numItems()-1);
	double sum=0.;
	for (int i=0; i<data->numEntries(); i++){
		double binCenter = data->get(i)->getRealValue("CMS_hgg_mass");
		double weight = data->weight();
		sum+=TMath::Log(TMath::Poisson(100.*weight,100.*pdfCurve->Eval(binCenter)));
	}
	return -1.*sum;
}

RooDataSet *stripWeights(RooDataSet *data, RooRealVar *var){

	RooDataSet *ret = new RooDataSet(Form("noweight_%s",data->GetName()),Form("noweight_%s",data->GetName()),RooArgSet(*var));
	for (int i=0; i<data->numEntries(); i++){
		double val = data->get(i)->getRealValue("CMS_hgg_mass");
		var->setVal(val);
		data->add(RooArgSet(*var));
	}
	return ret;
}

int main(int argc, char *argv[]){

	OptionParser(argc,argv);
	
	if (verbose_) std::cout << "[INFO] datfilename_	" << datfilename_ << std::endl;
	if (verbose_) std::cout << "[INFO] filename_	" << filename_ << std::endl;

	TStopwatch sw;
	sw.Start();

	RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
	RooMsgService::instance().setSilentMode(true);

	system(Form("mkdir -p %s/fTest",outdir_.c_str()));

	vector<string> procs;
	split(procs,procString_,boost::is_any_of(","));
	split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));

	if (isFlashgg_){
		ncats_ =flashggCats_.size();
		// Ensure that the loop over the categories does not go out of scope. 
	}

	TFile *inFile = TFile::Open(filename_.c_str());
	RooWorkspace *inWS;
	RooRealVar *mass; 
	if (isFlashgg_){
		if (verbose_) std::cout << "[INFO] Opening workspace tagsDumper/cms_hgg_13TeV"<<std::endl;
		inWS = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
		if (verbose_) std::cout << "[INFO] Workspace Open "<< inWS << std::endl;
		mass = (RooRealVar*)inWS->var("CMS_hgg_mass");
		if (verbose_) std::cout << "[INFO] Got mass var from ws"<<std::endl;
	} else {
		inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace"); 
		mass = (RooRealVar*)inWS->var("CMS_hgg_mass"); 
	}

	//mass->setBins(320);
	//mass->setRange(mass_-10,mass_+10);
	//mass->setBins(20);
	RooRealVar *MH = new RooRealVar("MH","MH",mass_);
	MH->setVal(mass_);
	MH->setConstant(true);

	map<string,pair<int,int> > choices;
	map<string,vector<RooPlot*> > plotsRV;
	map<string,vector<RooPlot*> > plotsWV;

	for (unsigned int p=0; p<procs.size(); p++){
		vector<RooPlot*> tempRV;
		vector<RooPlot*> tempWV;
		for (int cat=0; cat<ncats_; cat++){
			RooPlot *plotRV = mass->frame(Range(mass_-10,mass_+10));
			plotRV->SetTitle(Form("%s_cat%d_RV",procs[p].c_str(),cat));
			tempRV.push_back(plotRV);
			RooPlot *plotWV = mass->frame(Range(mass_-10,mass_+10));
			plotWV->SetTitle(Form("%s_cat%d_WV",procs[p].c_str(),cat));
			tempWV.push_back(plotWV);
		}
		plotsRV.insert(pair<string,vector<RooPlot*> >(procs[p],tempRV));
		plotsWV.insert(pair<string,vector<RooPlot*> >(procs[p],tempWV));
	}

	vector<int> colors;
	colors.push_back(kBlue);
	colors.push_back(kRed);
	colors.push_back(kGreen+2);
	colors.push_back(kMagenta+1);

	for (int cat=0; cat<ncats_; cat++){
		for (unsigned int p=0; p<procs.size(); p++){
			string proc = procs[p];
			RooDataSet *data;  
			RooDataSet *dataRV;
			RooDataSet *dataWV; 
			if (isFlashgg_){
				//		dataRV = (RooDataSet*)inWS->data(Form("%s_%d_13TeV_flashgg%s",proc.c_str(),mass_,flashggCats_[cat].c_str()));
				//		dataWV = (RooDataSet*)inWS->data(Form("%s_%d_13TeV_flashgg%s",proc.c_str(),mass_,flashggCats_[cat].c_str()));
				data   = (RooDataSet*)inWS->data(Form("%s_%d_13TeV_%s",proc.c_str(),mass_,flashggCats_[cat].c_str()));
				if (verbose_) {

					std::cout << "[INFO] Workspace contains : " << std::endl;
					std::list<RooAbsData*> data =  (inWS->allData()) ;
					for (std::list<RooAbsData*>::const_iterator iterator = data.begin(), end = data.end(); iterator != end; ++iterator) {
						std::cout << **iterator << std::endl;
					}


				}
				if (verbose_) std::cout << "[INFO] Retrieved combined RV/WV data "<< Form("%s_%d_13TeV_%s",proc.c_str(),mass_,flashggCats_[cat].c_str()) << "? "<< data<<std::endl;
				dataRV = new RooDataSet("dataRV","dataRV",&*data,*(data->get()),"dZ<1");
				if (verbose_) std::cout << "[INFO] Retrieved combined RV data"<<std::endl;
				dataWV = new RooDataSet("dataWV","dataWV",&*data,*(data->get()),"dZ>=1");
				if (verbose_) std::cout << "[INFO] Retrieved combined WV data"<<std::endl;
			} else {
				dataRV = (RooDataSet*)inWS->data(Form("sig_%s_mass_m%d_rv_cat%d",proc.c_str(),mass_,cat));
				dataWV = (RooDataSet*)inWS->data(Form("sig_%s_mass_m%d_wv_cat%d",proc.c_str(),mass_,cat));
			}
			//mass->setBins(160);
			//RooDataHist *dataRV = dataRVtemp->binnedClone();
			//RooDataHist *dataWV = dataWVtemp->binnedClone();
			//RooDataSet *dataRVw = (RooDataSet*)dataRVtemp->reduce(Form("CMS_hgg_mass>=%3d && CMS_hgg_mass<=%3d",mass_-10,mass_+10)); 
			//RooDataSet *dataWVw = (RooDataSet*)dataWVtemp->reduce(Form("CMS_hgg_mass>=%3d && CMS_hgg_mass<=%3d",mass_-10,mass_+10));
			//RooDataHist *dataRV = new RooDataHist(Form("roohist_%s",dataRVtemp->GetName()),Form("roohist_%s",dataRVtemp->GetName()),RooArgSet(*mass),*dataRVtemp);
			//RooDataHist *dataWV = new RooDataHist(Form("roohist_%s",dataWVtemp->GetName()),Form("roohist_%s",dataWVtemp->GetName()),RooArgSet(*mass),*dataWVtemp);
			//RooDataSet *dataRV = stripWeights(dataRVweight,mass);
			//RooDataSet *dataWV = stripWeights(dataWVweight,mass);
			//RooDataSet *data = (RooDataSet*)inWS->data(Form("sig_%s_mass_m%d_cat%d",proc.c_str(),mass_,cat));

			int rvChoice=0;
			int wvChoice=0;

			// right vertex
			int order=1;
			int prev_order=0;
			int cache_order=0;
			double thisNll=0.;
			//double prevNll=1.e6;
			double prevNll=0;
			double chi2=0.;
			double prob=0.;
			std::vector<pair<int,float> > rv_results;
			float rv_prob_limit =0.8;

			dataRV->plotOn(plotsRV[proc][cat]);
			while (prob<rv_prob_limit && order <5){ 
			//while (order<5) 
				RooAddPdf *pdf = buildSumOfGaussians(Form("cat%d_g%d",cat,order),mass,MH,order);
				RooFitResult *fitRes = pdf->fitTo(*dataRV,Save(true),/*SumW2Error(true),*/Verbose(false));//,Range(mass_-10,mass_+10));
				double myNll=0.;
				thisNll = fitRes->minNll();
				//double myNll = getMyNLL(mass,pdf,dataRV);
				//thisNll = getMyNLL(mass,pdf,dataRV);
				//RooAbsReal *nll = pdf->createNLL(*dataRV);
				//RooMinuit m(*nll);
				//m.migrad();
				//thisNll = nll->getVal();
				//plot(Form("plots/fTest/%s_cat%d_g%d_rv",proc.c_str(),cat,order),mass_,mass,dataRV,pdf);
				pdf->plotOn(plotsRV[proc][cat],LineColor(colors[order-1]));
				float chi2_bis= (plotsRV[proc][cat])->chiSquare();
				chi2 = 2.*(prevNll-thisNll);
				if (chi2<0. && order>1) chi2=0.;
				int diffInDof = (2*order+(order-1))-(2*prev_order+(prev_order-1));
			  //int diffInDof = (order- prev_order);
				//prob = TMath::Prob(chi2,diffInDof);
				float prob_old = TMath::Prob(chi2,diffInDof);
				prob = TMath::Prob(chi2_bis,2*order+(order-1));
				//Wilk's theorem
				cout << "[INFO] \t RV: proc " << proc << " cat " << cat << " order " << order << " diffinDof " << diffInDof << " prevNll " << prevNll << " this Nll " << thisNll << " myNll " << myNll << " chi2 " << chi2 << " chi2_bis " << chi2_bis<<  " prob_old " << prob_old << ", prob_new " <<  prob << endl;
				rv_results.push_back(std::make_pair(order,prob));
				prevNll=thisNll;
				cache_order=order;
				prev_order=order;
				order++;
			}
			if (prob <rv_prob_limit){
				float maxprob=-1;
				for(unsigned int i =0; i<rv_results.size(); i++){
					if (rv_results[i].second > maxprob){
				  maxprob=rv_results[i].second;
					rvChoice=rv_results[i].first;
					}
				}
			}else {
			rvChoice=cache_order;
			}

			// wrong vertex
			order=1;
			prev_order=0;
			cache_order=0;
			thisNll=0.;
			//prevNll=1.e6;
			prevNll=0;
			chi2=0.;
			prob=0.;
			std::vector<pair<int,float> > wv_results;
			float wv_prob_limit = 0.8;

			dataWV->plotOn(plotsWV[proc][cat]);
			//while (order<4) 
				while (prob<wv_prob_limit && order <4){ 
				RooAddPdf *pdf = buildSumOfGaussians(Form("cat%d_g%d",cat,order),mass,MH,order);
				RooFitResult *fitRes = pdf->fitTo(*dataWV,Save(true),/*SumW2Error(true),*/Verbose(false));//,Range(mass_-10,mass_+10));
				double myNll=0.;
				thisNll = fitRes->minNll();
				//double myNll = getMyNLL(mass,pdf,dataRV);
				//thisNll = getMyNLL(mass,pdf,dataRV);
				//RooAbsReal *nll = pdf->createNLL(*dataWV);
				//RooMinuit m(*nll);
				//m.migrad();
				//thisNll = nll->getVal();
				//plot(Form("plots/fTest/%s_cat%d_g%d_wv",proc.c_str(),cat,order),mass_,mass,dataWV,pdf);
				pdf->plotOn(plotsWV[proc][cat],LineColor(colors[order-1]));
				chi2 = 2.*(prevNll-thisNll);
				float chi2_bis= (plotsWV[proc][cat])->chiSquare();
				if (chi2<0. && order>1) chi2=0.;
				int diffInDof = (2*order+(order-1))-(2*prev_order+(prev_order-1));
				//int diffInDof = (order-prev_order);
				//prob = TMath::Prob(chi2,diffInDof);
				float prob_old = TMath::Prob(chi2,diffInDof);
				prob  = TMath::Prob(chi2_bis,2*order+(order-1));
				//Wilk's theorem
				cout << "[INFO] \t WV: proc " << proc <<" cat " << cat << " order " << order << " diffinDof " << diffInDof << " prevNll " << prevNll << " thosNll " << thisNll << " myNll" << myNll << " chi2" << chi2 << " chi2 bis " << chi2_bis << " prob_old " << prob_old << " prob_new " << prob <<  endl;
				wv_results.push_back(std::make_pair(order,prob));
				prevNll=thisNll;
				cache_order=order;
				prev_order=order;
				order++;
			}
			if (prob <wv_prob_limit){
				float maxprob=-1;
				for(unsigned int i =0; i<wv_results.size(); i++){
					if (wv_results[i].second > maxprob){
				  maxprob=wv_results[i].second;
					wvChoice=wv_results[i].first;
					}
				}
			}else {
			wvChoice=cache_order;
			}

			choices.insert(pair<string,pair<int,int> >(Form("%s %d",proc.c_str(),cat),make_pair(rvChoice,wvChoice)));
		} 
	}

	TLegend *leg = new TLegend(0.6,0.6,0.89,0.89);
	leg->SetFillColor(0);
	leg->SetLineColor(0);
	TH1F *h1 = new TH1F("h1","",1,0,1);
	h1->SetLineColor(colors[0]);
	leg->AddEntry(h1,"1st order","L");
	TH1F *h2 = new TH1F("h2","",1,0,1);
	h2->SetLineColor(colors[1]);
	leg->AddEntry(h2,"2nd order","L");
	TH1F *h3 = new TH1F("h3","",1,0,1);
	h3->SetLineColor(colors[2]);
	leg->AddEntry(h3,"3rd order","L");
	TH1F *h4 = new TH1F("h4","",1,0,1);
	h4->SetLineColor(colors[3]);
	leg->AddEntry(h4,"4th order","L");

	TCanvas *canv = new TCanvas();
	for (map<string,vector<RooPlot*> >::iterator plotIt=plotsRV.begin(); plotIt!=plotsRV.end(); plotIt++){
		string proc = plotIt->first;
		for (int cat=0; cat<ncats_; cat++){
			RooPlot *plot = plotIt->second.at(cat);
			plot->Draw();
			leg->Draw();
			canv->Print(Form("%s/fTest/rv_%s_cat%d.pdf",outdir_.c_str(),proc.c_str(),cat));
			canv->Print(Form("%s/fTest/rv_%s_cat%d.png",outdir_.c_str(),proc.c_str(),cat));
		}
	}
	for (map<string,vector<RooPlot*> >::iterator plotIt=plotsWV.begin(); plotIt!=plotsWV.end(); plotIt++){
		string proc = plotIt->first;
		for (int cat=0; cat<ncats_; cat++){
			RooPlot *plot = plotIt->second.at(cat);
			plot->Draw();
			leg->Draw();
			canv->Print(Form("%s/fTest/wv_%s_cat%d.pdf",outdir_.c_str(),proc.c_str(),cat));
			canv->Print(Form("%s/fTest/wv_%s_cat%d.png",outdir_.c_str(),proc.c_str(),cat));
		}
	}
	delete canv;

	cout << "[INFO] Recommended options" << endl;
	ofstream output_datfile;
	output_datfile.open ((datfilename_).c_str());
	if (verbose_) std::cout << "[INFO] Writing to datfilename_ " << datfilename_ << std::endl;
	output_datfile << "#proc cat nGausRV nGausWV" << std::endl;
	int p =0;
	for (map<string,pair<int,int> >::iterator it=choices.begin(); it!=choices.end(); it++){
		cout << "[INFO] \t "  <<" "<< it->first << " " << it->second.first << " " << it->second.second << endl;
		output_datfile<< it->first << " " << it->second.first << " " << it->second.second << endl;
		p++;
	}

	output_datfile.close();
	inFile->Close();
	return 0;
}
