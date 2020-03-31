void plot2D_kgkgam(){


  int ncontours = 999; 
  double stops[5]   = {0.0 ,  .1,   .25    , .5      , 1    };  
  double blue[5]    = {1.0 ,  1.  , 1  , 1           , 1.00   }; 
  double green[5]   = {0.25 , 0.3 ,   0.5  , 0.75    , 1.00   }; 
  double red [5]    = {0.1,  0.15 ,   0.4 , 0.6      , 1.00   }; 

  int npoints = 5; 

  TColor::CreateGradientColorTable(npoints, stops, red, green, blue, ncontours); 
  gStyle->SetNumberContours(ncontours); 

  TFile *f = TFile::Open("runFits_kappas/scan2D_statonly_kappa_g_vs_kappa_gam.root");
  TTree *limit = (TTree*) f->Get("limit");
  limit->Draw("2*deltaNLL:kappa_g:kappa_gam>>h4(100,0.4,1.6,100,0.5,2)","deltaNLL<10000", "prof colz");

  TH2F *h2D = (TH2F*) gROOT->FindObject("h4");
  h2D->SetContour(ncontours);

  TCanvas *can = new TCanvas("c","c",700,600);
  can->SetRightMargin(0.15);
  can->SetLeftMargin(0.115);
  can->SetBottomMargin(0.115);

  gStyle->SetOptStat(0);
  h2D->SetTitle("");
  h2D->Draw("colz");
  h2D->GetYaxis()->SetRangeUser(0.55,1.95);
  h2D->GetXaxis()->SetRangeUser(0.45,1.55);
  
  TH2F *c1 = (TH2F*) h2D->Clone();
  TH2F *c2 = (TH2F*) h2D->Clone();
  c1->SetContour(2); c1->SetContourLevel(1,2.3);
  c2->SetContour(2); c2->SetContourLevel(1,5.99);

  c1->SetLineWidth(3);
  c2->SetLineWidth(3);
  c1->SetLineColor(kBlack);
  c2->SetLineColor(kBlack);
  c2->SetLineStyle(2);
  c1->Draw("cont3same");
  c2->Draw("cont3same");

  h2D->SetMaximum(30);

  h2D->GetXaxis()->SetTitle("#kappa_{#gamma}");
  h2D->GetYaxis()->SetTitle("#kappa_{g}");
  h2D->GetXaxis()->SetTitleSize(0.055);
  h2D->GetYaxis()->SetTitleSize(0.055);
  h2D->GetZaxis()->SetTitleSize(0.035);
  h2D->GetZaxis()->SetTitle("-2 #Delta ln L");

  TGraph *gSM = new TGraph();
  gSM->SetPoint(0,1,1);
  gSM->SetMarkerStyle(34);
  gSM->SetMarkerSize(2.0);
  gSM->SetMarkerColor(kBlack);
  gSM->Draw("P");

  TLatex *lat =  new TLatex();
  lat->SetTextFont(42);
  lat->SetLineWidth(2);
  lat->SetTextAlign(11);
  lat->SetNDC();
  lat->SetTextSize(0.042);
  lat->DrawLatex(0.1,0.92,"#bf{CMS} #it{Preliminary}");
  lat->DrawLatex(0.69,0.92,"137 fb^{-1} (13#scale[0.75]{ }TeV)");

  TLegend *leg = new TLegend(0.55,0.66,0.8,0.86);
  leg->SetBorderSize(0);
  leg->SetFillColor(0);

  leg->AddEntry(gSM,  "SM"     , "P" );
  leg->AddEntry(c1,   "68% CL" , "L" );
  leg->AddEntry(c2,   "95% CL" , "L" );
  leg->Draw();

  can->SetTicky();
  can->SetTickx();
  can->RedrawAxis();
  can->Update(); 

  can->SaveAs("scan2D_statonly_kappa_g_vs_kappa_gam.pdf");
  can->SaveAs("scan2D_statonly_kappa_g_vs_kappa_gam.png");
}
