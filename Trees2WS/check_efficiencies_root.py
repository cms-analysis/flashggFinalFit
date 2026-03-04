import pandas as pd  

import ROOT

import glob
import argparse

parser=argparse.ArgumentParser()

parser.add_argument('--path')
parser.add_argument('--threshold',default=0.02)
parser.add_argument('--skipprocs',default=['THQ_FID','TTH_FWDH','THW_FID','VBF_1J','BBH_FWDH','GG2HQQ_FWDH','ZH2HQQ_FWDH','ZH2HNUNU_FWDH'],nargs='+',help="If procs too large for local memory, add here to skip")

args = parser.parse_args()

era=args.path.split('/')[-2]
if era=='preBPix':
    args.skipprocs+='GG2HNUNU_FWDH'
    args.skipprocs+='WPLUSH2HQQ_FWDH'
if era=='postBPix':
  
    args.skipprocs+='WPLUSH2HQQ_FWDH'

filelist=glob.glob(args.path+'/*')
flag=True
for file in filelist:
    if ('shortened' in file)|(any( [ i in file for i in args.skipprocs])):
        continue
    proc = file.split('/')[-1]
    files_proc=glob.glob(args.path+'/'+proc+'/nominal/*')
    files_proc_nominal=[]
    for i in files_proc:
        if ('_nominal' in i):
            files_proc_nominal.append(i)
    df=pd.DataFrame([])        
    for n in range(len(files_proc_nominal)):
        df=pd.concat([df,pd.read_parquet(files_proc_nominal[n])])

    # make sure no background included
    df=df[df.pred!=0]

    parquet_wsum=df.weight.sum()



    t=ROOT.TFile(args.path+'/'+proc+'/nominal/ws_'+proc+f'/output_{proc}_M125_pythia8_{proc}.root').Get('tagsDumper/cms_hgg_13TeV')
    
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
    # print(f'{proc}:   {wsum} {parquet_wsum}')
    
    try:
        assert abs(wsum - parquet_wsum)/parquet_wsum<args.threshold
        
    except:
        print(proc+':   '+str(abs(wsum - parquet_wsum)/parquet_wsum))
        flag=False

if flag==True:
    print('All sumw match in all processes between parquet and RooWS! ')


