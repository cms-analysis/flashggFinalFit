import pandas as pd
import ROOT
import glob 

lis = glob.glob('/eos/cms/store/group/phys_higgs/cmshgg/Run3HggSTXS_working/IA_nov2025/corrected/postEE/THW_FID/nominal/*nominal*parquet')
print(len(lis))


counter=0
wsum=0
for i in lis:
    if '_nomina' in i:
        new=pd.read_parquet(i)
        l = len(new)
        wsum_file=new.weight.sum()
        counter += l
        wsum += wsum_file
        print(wsum_file)
print(f'counter: {counter} wsum: {wsum}')


breakpoint()
t=ROOT.TFile('/eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src/flashggFinalFit/Workspaces_2dec/signal/postEE/output_THW_FID_M125_pythia8_THW_FID.root').Get('tagsDumper/cms_hgg_13TeV')
    
all_datasets = [k.GetName() for k in t.allData()]

wsum=0
counter=0
for i in all_datasets:
    
    Data=t.data(i)
    if Data and Data.ClassName() == "RooDataSet":
        for j in range(Data.numEntries()):
            entry=Data.get(j)
            w=Data.weight()
            wsum+=w
            counter+=1
print(f'wsum: {wsum} count: {counter}')